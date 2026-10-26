# How to add a tool

## Layout

One file per tool, plus an aggregator that re-exports them:

```
app/tools/<domain>/
  __init__.py
  get_salary.py               # schemas + function + TOOLS
  request_salary_change.py
  get_pending_salary.py
  _shared.py                  # optional: constants shared by the tools
  tools.py                    # imports the per-tool TOOLS lists
```

## Steps

1. Create `app/tools/<domain>/<tool_name>.py`.
2. Define the Pydantic input/output schemas.
3. Implement a plain Python function.
4. Export a module-level `TOOLS` list holding the tool's `ToolSpec`.
5. Import that list in `app/tools/<domain>/tools.py` and add it to the
   aggregated `TOOLS`.
6. The `ToolRegistry` auto-discovers it on import.
7. Add the tool name to the relevant agent's `tools` list in
   `app/agents/registry.py`.
8. If the tool mutates state, set `requires_approval=True`.

`ToolRegistry.discover()` registers a spec only once even when the aggregator
re-exports it, but two *distinct* specs sharing a name still raise
`Duplicate tool name`.
