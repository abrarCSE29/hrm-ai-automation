"""Convert framework-agnostic ToolSpecs to Agno Function objects."""


from agno.tools.function import Function

from app.tools.base import ToolSpec
from app.tools.execution import execute_tool
from app.tools.registry import registry


def spec_to_agno_function(spec: ToolSpec, agent_name: str) -> Function:
    schema = spec.input_schema.model_json_schema()

    def entrypoint(**kwargs):
        return execute_tool(spec, kwargs, agent_name=agent_name)

    return Function(
        name=spec.name,
        description=spec.description,
        entrypoint=entrypoint,
        parameters=schema,
        skip_entrypoint_processing=True,
    )


def build_tools_for_agent(agent_name: str, allowed_tool_names: list[str]) -> list[Function]:
    tools = []
    for name in allowed_tool_names:
        spec = registry.get(name)
        tools.append(spec_to_agno_function(spec, agent_name))
    return tools
