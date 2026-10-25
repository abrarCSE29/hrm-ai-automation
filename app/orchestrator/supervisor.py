"""Supervisor routing (Agno Team in route mode)."""

from agno.team import Team, TeamMode

from app.agents.factory import build_all_specialists
from app.core.config import settings
from app.core.models import get_chat_model
from app.core.observability import trace_run


def build_supervisor(env: str | None = None, model=None):
    supervisor_model = model if model is not None else get_chat_model(env)
    specialists = build_all_specialists(env, model=model)
    team = Team(
        name="hrm_supervisor",
        mode=TeamMode.route,
        model=supervisor_model,
        members=specialists,
        instructions=[
            (
                "You are an HR (Human Resources) assistant for the HRM automation system. "
                "Introduce yourself as an HR assistant when asked who you are."
            ),
            "Route the user request to the most appropriate specialist agent.",
            "For leave balance or leave requests, route to leave_agent.",
        ],
    )
    return team


def run_chat(
    message: str,
    env: str | None = None,
    model=None,
    conversation_id: str | None = None,
    user_id: str | None = None,
    trace_id: str | None = None,
) -> str:
    env = env or settings.ENVIRONMENT
    if model is not None:
        try:
            from app.core.observability import is_tracing_enabled

            if is_tracing_enabled():
                from app.core.models import _patch_model_for_tracing

                model = _patch_model_for_tracing(model)
        except Exception:  # noqa: BLE001, S110
            pass
    team = build_supervisor(env, model=model)

    from app.core.observability import is_tracing_enabled

    if not is_tracing_enabled():
        result = team.run(message)
        content = getattr(result, "content", None)
        if content is None:
            content = str(result)
        return content

    with trace_run(
        "hrm_chat_turn",
        run_type="chain",
        inputs={"message": message},
        metadata={
            "conversation_id": conversation_id or "",
            "trace_id": trace_id or "",
            "user_id": user_id or "",
            "environment": env,
        },
        tags=["hrm", "chat"],
    ) as run:
        result = team.run(message)
        content = getattr(result, "content", None)
        if content is None:
            content = str(result)
        if run is not None:
            run.outputs = {"response": content}
        return content
