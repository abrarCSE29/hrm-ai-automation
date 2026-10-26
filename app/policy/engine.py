"""Deterministic policy engine."""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Decision:
    allowed: bool
    reasons: list[str] = field(default_factory=list)


class PolicyRule(Protocol):
    def evaluate(self, action: str, args: dict) -> str | None:
        """Return a reason string if violated, else None."""
        ...


class PolicyEngine:
    def __init__(self, rules: list[PolicyRule] | None = None):
        self.rules = rules or []

    def validate(self, action: str, args: dict) -> Decision:
        reasons = []
        for rule in self.rules:
            reason = rule.evaluate(action, args or {})
            print(reason)
            if reason:
                reasons.append(reason)
                
        print(len(reasons))
        return Decision(allowed=len(reasons) == 0, reasons=reasons)
