import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.approval.schemas import ApprovalDecisionIn, ApprovalOut
from app.approval.service import approve, list_pending, reject
from app.core.config import settings
from app.core.trace import new_trace_id, set_trace_context
from app.db.models import Approval
from app.db.session import get_db
from app.interfaces.api.schemas import ChatRequest, ChatResponse, HealthResponse
from app.orchestrator.supervisor import run_chat

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", environment=settings.ENVIRONMENT)


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):  # noqa: B008
    trace_id = new_trace_id()
    conversation_id = req.conversation_id or uuid.uuid4().hex
    set_trace_context(trace_id, conversation_id, req.message)

    # ensure conversation row exists (best-effort)
    from app.db.models import Conversation

    try:
        exists = db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
        if exists is None:
            db.add(Conversation(conversation_id=conversation_id, user_id=req.user_id))
            db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()

    response = run_chat(
        req.message,
        conversation_id=conversation_id,
        user_id=req.user_id,
        trace_id=trace_id,
    )
    return ChatResponse(trace_id=trace_id, conversation_id=conversation_id, response=response)


def _approval_out(a: Approval) -> ApprovalOut:
    return ApprovalOut(
        approval_id=a.approval_id,
        trace_id=a.trace_id,
        conversation_id=a.conversation_id,
        agent_name=a.agent_name,
        tool_name=a.tool_name,
        args=a.args or {},
        reasoning=a.reasoning,
        risk_level=a.risk_level,
        status=a.status,
        created_at=a.created_at,
    )


@router.get("/approvals/pending", response_model=list[ApprovalOut])
def approvals_pending(db: Session = Depends(get_db)):  # noqa: B008
    return [_approval_out(a) for a in list_pending(db)]


@router.post("/approvals/{approval_id}/approve")
def approvals_approve(approval_id: str, body: ApprovalDecisionIn, db: Session = Depends(get_db)):  # noqa: B008
    try:
        approval, result = approve(db, approval_id, decided_by=body.decided_by, note=body.note)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"approval_id": approval.approval_id, "status": approval.status, "result": result}


@router.post("/approvals/{approval_id}/reject")
def approvals_reject(approval_id: str, body: ApprovalDecisionIn, db: Session = Depends(get_db)):  # noqa: B008
    try:
        approval = reject(db, approval_id, decided_by=body.decided_by, note=body.note)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"approval_id": approval.approval_id, "status": approval.status}
