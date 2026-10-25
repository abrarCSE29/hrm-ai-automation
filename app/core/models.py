"""Environment-driven model provider factory.

All Agno imports are intentionally isolated here (plus app/agents and app/orchestrator).
"""

from collections.abc import Callable

from app.core.config import get_model_pair_config, settings


# Lazy imports keep import-time cost low and make mocking easier.
def _groq_model(model_id: str):
    from agno.models.groq import Groq

    return Groq(id=model_id, api_key=settings.GROQ_API_KEY)


def _openai_model(model_id: str):
    from agno.models.openai import OpenAIChat

    return OpenAIChat(id=model_id, api_key=settings.OPENAI_API_KEY)


_PROVIDER_FACTORIES = {
    "dev": _groq_model,
    "production": _openai_model,
    "prod": _openai_model,
}


def get_chat_model(env: str | None = None, *, fallback: bool = False):
    """Return a configured Agno model instance for the given environment.

    ``env`` defaults to the ENVIRONMENT setting. ``fallback=True`` selects the
    fallback model id (if configured) instead of the primary.
    """
    env = (env or settings.ENVIRONMENT or "dev").lower()
    # normalize
    if env == "prod":
        env = "production"

    if env not in _PROVIDER_FACTORIES:
        # Unknown environment falls back to dev/Groq, but keep config extensible.
        env = "dev"

    cfg = get_model_pair_config(env)
    model_id = cfg["fallback"] if fallback and cfg.get("fallback") else cfg["primary"]
    if fallback and not cfg.get("fallback"):
        model_id = cfg["primary"]

    factory = _PROVIDER_FACTORIES[env]
    model = factory(model_id)

    # Optionally wrap for LangSmith tracing (real LLM call spans).
    try:
        from app.core.observability import is_tracing_enabled

        if is_tracing_enabled():
            model = _patch_model_for_tracing(model)
    except Exception:  # noqa: BLE001, S110
        pass

    return model


def get_model_candidates(env: str | None = None):
    """Primary then fallback (if configured) model instances."""
    env = (env or settings.ENVIRONMENT or "dev").lower()
    if env == "prod":
        env = "production"
    cfg = get_model_pair_config(env)
    out = [get_chat_model(env, fallback=False)]
    if cfg.get("fallback"):
        out.append(get_chat_model(env, fallback=True))
    return out


def run_with_fallback(operation: Callable, env: str | None = None):
    """Run ``operation(model)`` with primary, retrying once on the fallback.

    ``operation`` is a callable accepting a model instance and returning a result.
    """
    env = (env or settings.ENVIRONMENT or "dev").lower()
    if env == "prod":
        env = "production"

    primary = get_chat_model(env, fallback=False)
    try:
        return operation(primary)
    except Exception:
        cfg = get_model_pair_config(env)
        if not cfg.get("fallback"):
            raise
        fallback_model = get_chat_model(env, fallback=True)
        if fallback_model is primary:
            raise
        return operation(fallback_model)


def provider_class_for(env: str) -> type:
    """Helper used by tests to assert the factory's provider class."""
    model = get_chat_model(env, fallback=False)
    return type(model)


def _serialize_messages(messages) -> list:
    out = []
    for m in messages or []:
        out.append({"role": getattr(m, "role", None), "content": getattr(m, "content", None)})
    return out


def _usage_from_response(response) -> dict:
    usage = {}
    for attr in ("input_tokens", "output_tokens", "total_tokens", "cache_read_tokens", "reasoning_tokens"):
        val = getattr(response, attr, None)
        if val is not None:
            usage[attr] = val
    response_usage = getattr(response, "response_usage", None)
    if response_usage is not None:
        for attr in ("input_tokens", "output_tokens", "total_tokens", "cache_read_tokens", "reasoning_tokens"):
            val = getattr(response_usage, attr, None)
            if val is not None and attr not in usage:
                usage[attr] = val
    return usage


def _provider_name(model) -> str:
    module = type(model).__module__.lower()
    if "groq" in module:
        return "groq"
    return "openai"


def _patch_model_for_tracing(model):
    if getattr(model, "_hrm_traced", False):
        return model

    original_invoke = model.invoke
    original_ainvoke = model.ainvoke

    def traced_invoke(*args, **kwargs):
        from app.core.observability import is_tracing_enabled, trace_run

        if not is_tracing_enabled():
            return original_invoke(*args, **kwargs)

        messages = kwargs.get("messages")
        with trace_run(
            "llm",
            run_type="llm",
            inputs={"messages": _serialize_messages(messages)},
            metadata={"ls_provider": _provider_name(model), "ls_model_name": getattr(model, "id", None)},
            tags=["hrm", "llm"],
        ) as run:
            result = original_invoke(*args, **kwargs)
            if run is not None:
                run.outputs = {"content": getattr(result, "content", None), "tool_calls": getattr(result, "tool_calls", None)}
                usage = _usage_from_response(result)
                if usage and any(v for v in usage.values()):
                    run.extra = {"usage_metadata": usage}
            return result

    async def traced_ainvoke(*args, **kwargs):
        from app.core.observability import is_tracing_enabled, trace_run

        if not is_tracing_enabled():
            return await original_ainvoke(*args, **kwargs)

        messages = kwargs.get("messages")
        with trace_run(
            "llm",
            run_type="llm",
            inputs={"messages": _serialize_messages(messages)},
            metadata={"ls_provider": _provider_name(model), "ls_model_name": getattr(model, "id", None)},
            tags=["hrm", "llm"],
        ) as run:
            result = await original_ainvoke(*args, **kwargs)
            if run is not None:
                run.outputs = {"content": getattr(result, "content", None), "tool_calls": getattr(result, "tool_calls", None)}
                usage = _usage_from_response(result)
                if usage and any(v for v in usage.values()):
                    run.extra = {"usage_metadata": usage}
            return result

    model.invoke = traced_invoke
    model.ainvoke = traced_ainvoke
    model._hrm_traced = True
    return model
