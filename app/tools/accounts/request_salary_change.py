"""Request a salary change tool (framework-agnostic)."""

import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.db.models import Salary, SalaryChangeRequest
from app.db.session import SessionLocal
from app.tools.accounts._shared import DEMO_SALARIES
from app.tools.base import ToolSpec


class RequestSalaryChangeInput(BaseModel):
    employee_id: str = Field(..., description="Employee identifier")
    new_salary: float = Field(..., gt=0, description="Requested new salary amount")
    reason: str = Field("", description="Reason for the salary change request")


class RequestSalaryChangeOutput(BaseModel):
    request_id: str
    employee_id: str
    current_salary: float
    requested_salary: float
    status: str


def request_salary_change(employee_id: str, new_salary: float, reason: str = "") -> dict:
    """Request a salary change (applied after approval)."""
    db = SessionLocal()
    try:
        row = db.query(Salary).filter(Salary.employee_id == employee_id).first()
        current = float(row.amount) if row is not None else DEMO_SALARIES.get(employee_id, 0.0)
        request_id = f"SCR-{uuid.uuid4().hex[:8]}"
        change = SalaryChangeRequest(
            request_id=request_id,
            employee_id=employee_id,
            current_salary=current,
            requested_salary=new_salary,
            reason=reason,
            status="approved",
            decided_at=datetime.now(UTC),
            decided_by="approval_flow",
        )
        db.add(change)
        if row is not None:
            row.amount = new_salary
        else:
            db.add(Salary(employee_id=employee_id, amount=new_salary, currency="BDT", effective_date=None))
        db.commit()
        return {
            "request_id": request_id,
            "employee_id": employee_id,
            "current_salary": current,
            "requested_salary": new_salary,
            "status": "approved",
        }
    finally:
        db.close()


TOOLS = [
    ToolSpec(
        name="request_salary_change",
        description="Request a salary increase or decrease for an employee (requires approval).",
        func=request_salary_change,
        input_schema=RequestSalaryChangeInput,
        output_schema=RequestSalaryChangeOutput,
        requires_approval=True,
        risk_level="high",
        sensitive_fields=["employee_id"],
        domain="accounts",
    )
]
