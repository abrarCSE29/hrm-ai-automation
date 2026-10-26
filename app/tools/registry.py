"""Auto-discovering tool registry (framework-agnostic)."""

import importlib
import pkgutil

from app.tools.base import ToolSpec


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"Duplicate tool name: {spec.name}")
        self._tools[spec.name] = spec

    def discover(self, package_name: str = "app.tools") -> None:
        package = importlib.import_module(package_name)
        # A ToolSpec object can surface twice: once from the module that defines
        # it and once from an aggregating ``<domain>/tools.py`` that re-exports
        # it. That is one tool, not a duplicate. Only two *distinct* specs
        # sharing a name are an error.
        seen: set[int] = set()

        def register_once(spec: ToolSpec) -> None:
            if id(spec) in seen:
                return
            seen.add(id(spec))
            self.register(spec)

        for module_info in pkgutil.walk_packages(package.__path__, prefix=package_name + "."):
            # skip base/registry modules
            if module_info.name.endswith(("base", "registry")):
                continue
            try:
                module = importlib.import_module(module_info.name)
            except Exception:  # noqa: BLE001, S112
                continue
            tools = getattr(module, "TOOLS", None)
            if tools:
                for spec in tools:
                    register_once(spec)
            # also support decorator-registered specs
            for attr in vars(module).values():
                if isinstance(attr, ToolSpec):
                    register_once(attr)

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def specs_for(self, names: list[str]) -> list[ToolSpec]:
        return [self.get(n) for n in names]

    def redact(self, tool_name: str, args: dict) -> dict:
        try:
            spec = self.get(tool_name)
        except KeyError:
            return dict(args)
        sensitive = set(spec.sensitive_fields)
        out = {}
        for k, v in args.items():
            out[k] = "[REDACTED]" if k in sensitive else v
        return out


# module-level singleton used by agents
registry = ToolRegistry()
registry.discover()
