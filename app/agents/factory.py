"""Build Agno agents from registry specs."""

from agno.agent import Agent

from app.agents.registry import AgentSpec
from app.agents.tool_adapter import build_tools_for_agent
from app.core.models import get_chat_model


def build_specialist_agent(spec: AgentSpec, env: str | None = None, model=None) -> Agent:
    model = model if model is not None else get_chat_model(env)
    tools = build_tools_for_agent(spec.name, spec.tools)
    return Agent(
        name=spec.name,
        role=spec.role,
        model=model,
        tools=tools,
        instructions=[spec.role],
        markdown=True,
    )


def build_all_specialists(env: str | None = None, model=None):
    from app.agents.registry import AGENT_REGISTRY

    return [build_specialist_agent(spec, env, model=model) for spec in AGENT_REGISTRY]
