"""Get pending salary tool (framework-agnostic)."""

from pydantic import BaseModel, Field

from app.db.models import PendingSalary
from app.db.session import SessionLocal
from app.tools.base import ToolSpec


class PendingSalaryInput(BaseModel):
    employee_id: str = Field(..., description="Employee identifier")


class PendingSalaryOutput(BaseModel):
    employee_id: str
    pending_salary: float
    items: list[dict]


def get_pending_salary(employee_id: str) -> dict:
    """Return pending (owed) salary amount for an employee."""
    db = SessionLocal()
    try:
        rows = db.query(PendingSalary).filter(PendingSalary.employee_id == employee_id, PendingSalary.status == "pending").all()
        items = [{"id": r.id, "amount": float(r.amount or 0.0), "description": r.description, "due_date": r.due_date} for r in rows]
        total = float(sum(i["amount"] for i in items))
        return {"employee_id": employee_id, "pending_salary": total, "items": items}
    finally:
        db.close()


TOOLS = [
    ToolSpec(
        name="get_pending_salary",
        description="Get pending salary amount owed to an employee by the company.",
        func=get_pending_salary,
        input_schema=PendingSalaryInput,
        output_schema=PendingSalaryOutput,
        requires_approval=False,
        risk_level="low",
        sensitive_fields=["employee_id"],
        domain="accounts",
    )
]
