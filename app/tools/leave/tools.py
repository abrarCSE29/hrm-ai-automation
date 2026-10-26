"""Leave management tools (framework-agnostic)."""

from typing import Literal

from pydantic import BaseModel, Field

from app.db.models import Approval
from app.db.session import SessionLocal
from app.tools.base import ToolSpec


class LeaveBalanceInput(BaseModel):
    employee_id: str = Field(..., description="Employee identifier")


class LeaveBalanceOutput(BaseModel):
    employee_id: str
    annual_remaining: int
    sick_remaining: int
    casual_remaining: int


def get_leave_balance(employee_id: str) -> dict:
    """Return the current leave balance for an employee (demo data)."""
    # Demo implementation; replace with DB lookup in production.
    return {
        "employee_id": employee_id,
        "annual_remaining": 12,
        "sick_remaining": 6,
        "casual_remaining": 4,
    }


class SubmitLeaveRequestInput(BaseModel):
    employee_id: str = Field(..., description="Employee identifier")
    leave_type: Literal["annual", "sick", "casual"] = Field(..., description="Type of leave")
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")
    reason: str = Field("", description="Reason for leave")
    days: int = Field(..., ge=1, description="Number of leave days requested")


class SubmitLeaveRequestOutput(BaseModel):
    request_id: str
    employee_id: str
    status: str
    days: int


def submit_leave_request(
    employee_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str = "",
    days: int = 1,
) -> dict:
    """Submit a leave request (demo)."""
    return {
        "request_id": f"LR-{employee_id}-{start_date}",
        "employee_id": employee_id,
        "status": "submitted",
        "days": days,
    }


class PendingLeaveRequestsInput(BaseModel):
    employee_id: str = Field("", description="Optional employee identifier filter")


class PendingLeaveRequestsOutput(BaseModel):
    requests: list[dict]
    count: int


def get_pending_leave_requests(employee_id: str = "") -> dict:
    """Return pending leave requests (awaiting approval)."""
    db = SessionLocal()
    try:
        rows = db.query(Approval).filter(Approval.tool_name == "submit_leave_request", Approval.status == "pending").all()
        requests = []
        for r in rows:
            args = r.args or {}
            if employee_id and args.get("employee_id") != employee_id:
                continue
            requests.append(
                {
                    "approval_id": r.approval_id,
                    "employee_id": args.get("employee_id"),
                    "leave_type": args.get("leave_type"),
                    "start_date": args.get("start_date"),
                    "end_date": args.get("end_date"),
                    "days": args.get("days"),
                    "reason": args.get("reason"),
                    "status": r.status,
                }
            )
        return {"requests": requests, "count": len(requests)}
    finally:
        db.close()


TOOLS = [
    ToolSpec(
        name="get_leave_balance",
        description="Get the current leave balance for an employee.",
        func=get_leave_balance,
        input_schema=LeaveBalanceInput,
        output_schema=LeaveBalanceOutput,
        requires_approval=False,
        risk_level="low",
        sensitive_fields=[],
        domain="leave",
    ),
    ToolSpec(
        name="submit_leave_request",
        description="Submit a leave request for an employee.",
        func=submit_leave_request,
        input_schema=SubmitLeaveRequestInput,
        output_schema=SubmitLeaveRequestOutput,
        requires_approval=True,
        risk_level="medium",
        sensitive_fields=["employee_id"],
        domain="leave",
    ),
    ToolSpec(
        name="get_pending_leave_requests",
        description="Get pending leave requests awaiting approval.",
        func=get_pending_leave_requests,
        input_schema=PendingLeaveRequestsInput,
        output_schema=PendingLeaveRequestsOutput,
        requires_approval=False,
        risk_level="low",
        sensitive_fields=["employee_id"],
        domain="leave",
    ),
]
