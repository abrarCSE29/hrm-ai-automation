from agno.models.response import ModelResponse

from app.agents.mock_model import MockModel
from app.approval.service import approve, list_pending
from app.db.models import AuditLog
from app.orchestrator.supervisor import run_chat


def test_approval_flow_blocks_until_approved(db):
    model = MockModel(
        responses=[
            ModelResponse(
                tool_calls=[
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {
                            "name": "delegate_task_to_member",
                            "arguments": '{"member_id": "leave-agent", "task": "Submit leave request"}',
                        },
                    }
                ]
            ),
            ModelResponse(
                tool_calls=[
                    {
                        "id": "c2",
                        "type": "function",
                        "function": {
                            "name": "submit_leave_request",
                            "arguments": '{"employee_id": "E001", "leave_type": "annual", "start_date": "2026-11-01", "end_date": "2026-11-03", "reason": "vacation", "days": 3}',
                        },
                    }
                ]
            ),
            ModelResponse(content="Your leave request is pending approval."),
        ]
    )
    run_chat("Submit a leave request for 3 days", model=model)

    pending = list_pending(db)
    assert len(pending) == 1
    approval_id = pending[0].approval_id

    # not executed yet (no audit executed? check approvals status)
    assert pending[0].status == "pending"

    approval, result = approve(db, approval_id)
    assert approval.status == "approved"
    assert result.get("status") == "submitted"

    # audit entries exist
    audits = db.query(AuditLog).all()
    assert len(audits) >= 2
    assert any(a.final_outcome == "pending_approval" for a in audits)
    assert any(a.final_outcome == "executed" for a in audits)
