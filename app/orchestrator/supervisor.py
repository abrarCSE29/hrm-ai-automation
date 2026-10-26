"""Supervisor routing (Agno Team in route mode)."""

from agno.team import Team, TeamMode

from app.agents.factory import build_all_specialists
from app.core.config import settings
from app.core.models import _patch_model_for_tracing, get_chat_model
from app.core.observability import is_tracing_enabled, trace_run


def build_supervisor(env: str | None = None, model=None):
    model = model if model is not None else get_chat_model(env)
    return Team(
        name="hrm_supervisor",
        mode=TeamMode.route,
        model=model,
        members=build_all_specialists(env, model=model),
        instructions=[
            (
                "You are an HR (Human Resources) assistant for the HRM automation system. "
                "Introduce yourself as an HR assistant when asked who you are."
            ),
            "Route the user request to the most appropriate specialist agent.",
            "For leave balance or leave requests, route to leave_agent.",
            "For salary, accounts, or pending salary questions, route to account_agent.",
        ],
    )


def run_chat(
    message: str,
    env: str | None = None,
    model=None,
    conversation_id: str | None = None,
    user_id: str | None = None,
    trace_id: str | None = None,
) -> str:
    env = env or settings.ENVIRONMENT
    if model is not None and is_tracing_enabled():
        model = _patch_model_for_tracing(model)
    team = build_supervisor(env, model=model)

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
