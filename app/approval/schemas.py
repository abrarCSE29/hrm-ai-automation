from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ApprovalOut(BaseModel):
    approval_id: str
    trace_id: str
    conversation_id: str
    agent_name: str
    tool_name: str
    args: dict[str, Any]
    reasoning: str
    risk_level: str
    status: str
    created_at: datetime


class ApprovalDecisionIn(BaseModel):
    decided_by: str = "human"
    note: str | None = None
