# How to add a tool

1. Create `app/tools/<domain>/tools.py`.
2. Define Pydantic input/output schemas.
3. Implement a plain Python function.
4. Append a `ToolSpec` to the module-level `TOOLS` list.
5. The `ToolRegistry` auto-discovers it on import.
6. Add the tool name to the relevant agent's `tools` list in `app/agents/registry.py`.
7. If the tool mutates state, set `requires_approval=True`.
