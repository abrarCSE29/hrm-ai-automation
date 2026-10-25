"""Approval queue service."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.trace import get_conversation_id, get_trace_id, get_user_input
from app.db.models import Approval, AuditLog
from app.tools.registry import registry


def _redact(tool_name: str, args: dict) -> dict:
    return registry.redact(tool_name, args)


def create_pending_approval(
    db: Session,
    *,
    tool_name: str,
    args: dict,
    reasoning: str = "",
    risk_level: str = "low",
    agent_name: str = "",
    trace_id: str | None = None,
    conversation_id: str | None = None,
) -> Approval:
    trace_id = trace_id or get_trace_id()
    conversation_id = conversation_id or get_conversation_id()
    approval = Approval(
        approval_id=uuid.uuid4().hex,
        trace_id=trace_id,
        conversation_id=conversation_id,
        agent_name=agent_name,
        tool_name=tool_name,
        args=args,
        reasoning=reasoning,
        risk_level=risk_level,
        status="pending",
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


def list_pending(db: Session) -> list[Approval]:
    return db.query(Approval).filter(Approval.status == "pending").order_by(Approval.created_at.desc()).all()


def get_approval(db: Session, approval_id: str) -> Approval | None:
    return db.query(Approval).filter(Approval.approval_id == approval_id).first()


def approve(db: Session, approval_id: str, decided_by: str = "human", note: str | None = None) -> tuple[Approval, dict]:
    approval = get_approval(db, approval_id)
    if approval is None:
        raise ValueError("approval not found")
    if approval.status != "pending":
        raise ValueError(f"approval already {approval.status}")
    approval.status = "approved"
    approval.decided_by = decided_by
    approval.decision_note = note
    approval.decided_at = datetime.now(UTC)
    db.commit()
    db.refresh(approval)

    # execute synchronously
    spec = registry.get(approval.tool_name)
    result = spec.func(**(approval.args or {}))

    # audit
    audit(
        db,
        trace_id=approval.trace_id,
        conversation_id=approval.conversation_id,
        agent_name=approval.agent_name,
        user_input=get_user_input(),
        tool_called=approval.tool_name,
        tool_args=_redact(approval.tool_name, approval.args or {}),
        policy_decision="approved_previously",
        approval_decision="approved",
        final_outcome="executed",
    )
    return approval, (result if isinstance(result, dict) else {"result": result})


def reject(db: Session, approval_id: str, decided_by: str = "human", note: str | None = None) -> Approval:
    approval = get_approval(db, approval_id)
    if approval is None:
        raise ValueError("approval not found")
    if approval.status != "pending":
        raise ValueError(f"approval already {approval.status}")
    approval.status = "rejected"
    approval.decided_by = decided_by
    approval.decision_note = note
    approval.decided_at = datetime.now(UTC)
    db.commit()
    db.refresh(approval)
    audit(
        db,
        trace_id=approval.trace_id,
        conversation_id=approval.conversation_id,
        agent_name=approval.agent_name,
        user_input=get_user_input(),
        tool_called=approval.tool_name,
        tool_args=_redact(approval.tool_name, approval.args or {}),
        policy_decision="n/a",
        approval_decision="rejected",
        final_outcome="rejected",
    )
    return approval


def audit(
    db: Session,
    *,
    trace_id: str,
    conversation_id: str = "",
    agent_name: str = "",
    user_input: str = "",
    tool_called: str = "",
    tool_args: dict | None = None,
    policy_decision: str = "",
    approval_decision: str = "",
    final_outcome: str = "",
) -> None:
    entry = AuditLog(
        trace_id=trace_id,
        conversation_id=conversation_id,
        agent_name=agent_name,
        user_input=user_input,
        tool_called=tool_called,
        tool_args=tool_args or {},
        policy_decision=policy_decision,
        approval_decision=approval_decision,
        final_outcome=final_outcome,
    )
    db.add(entry)
    db.commit()
