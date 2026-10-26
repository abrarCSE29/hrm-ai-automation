"""Get employee salary tool (framework-agnostic)."""

from pydantic import BaseModel, Field

from app.db.models import Employee, Salary
from app.db.session import SessionLocal
from app.tools.accounts._shared import DEMO_SALARIES
from app.tools.base import ToolSpec


class SalaryInput(BaseModel):
    employee_id: str = Field(..., description="Employee identifier")


class SalaryOutput(BaseModel):
    employee_id: str
    amount: float
    currency: str


def get_salary(employee_id: str) -> dict:
    """Return the current salary for an employee."""
    db = SessionLocal()
    try:
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        row = db.query(Salary).filter(Salary.employee_id == employee_id).first()
        if emp is None and row is None:
            return {"employee_id": employee_id, "amount": 0.0, "currency": "BDT", "found": False, "message": "employee not found"}
        amount = float(row.amount or 0.0) if row is not None else DEMO_SALARIES.get(employee_id, 0.0)
        currency = (row.currency if row is not None else "BDT") or "BDT"
        return {"employee_id": employee_id, "amount": amount, "currency": currency, "found": True}
    finally:
        db.close()


TOOLS = [
    ToolSpec(
        name="get_salary",
        description="Get the current salary for an employee.",
        func=get_salary,
        input_schema=SalaryInput,
        output_schema=SalaryOutput,
        requires_approval=False,
        risk_level="low",
        sensitive_fields=["employee_id"],
        domain="accounts",
    )
]
