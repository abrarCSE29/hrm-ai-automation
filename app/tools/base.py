"""Framework-agnostic tool definitions."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

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


@dataclass
class ToolResult:
    status: str  # ok | pending_approval | policy_denied | error
    data: Any = None
    approval_id: str | None = None
    message: str = ""
    policy_reasons: list[str] = field(default_factory=list)
