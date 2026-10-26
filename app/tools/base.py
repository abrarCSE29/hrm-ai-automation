"""Framework-agnostic tool definitions."""

from collections.abc import Callable
from dataclasses import dataclass, field

from pydantic import BaseModel


@dataclass
class ToolSpec:
    name: str
    description: str
    func: Callable
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]
    requires_approval: bool = False
    risk_level: str = "low"
    sensitive_fields: list[str] = field(default_factory=list)
    domain: str = ""
