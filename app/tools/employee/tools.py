"""Employee tools (framework-agnostic)."""

from pydantic import BaseModel, Field

from app.db.models import Employee, PendingSalary, Salary
from app.db.session import SessionLocal
from app.tools.base import ToolSpec

DEMO_EMPLOYEES = {
    "E001": {"name": "Alice", "email": "alice@example.com", "department": "Engineering", "manager_id": "MGR-001"},
    "E002": {"name": "Bob", "email": "bob@example.com", "department": "HR", "manager_id": "MGR-002"},
}


class EmployeeProfileInput(BaseModel):
    employee_id: str = Field(..., description="Employee identifier")


class EmployeeProfileOutput(BaseModel):
    employee_id: str
    name: str
    email: str
    department: str
    manager_id: str | None
    salary: float | None
    pending_salary: float
    found: bool


def get_employee_profile(employee_id: str) -> dict:
    """Return all information related to an employee."""
    db = SessionLocal()
    try:
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if emp is not None:
            salary_row = db.query(Salary).filter(Salary.employee_id == employee_id).first()
            pending_rows = db.query(PendingSalary).filter(PendingSalary.employee_id == employee_id, PendingSalary.status == "pending").all()
            return {
                "employee_id": emp.employee_id,
                "name": emp.name,
                "email": emp.email,
                "department": emp.department,
                "manager_id": emp.manager_id,
                "salary": float(salary_row.amount) if salary_row is not None else None,
                "pending_salary": float(sum(r.amount or 0 for r in pending_rows)),
                "found": True,
            }
        demo = DEMO_EMPLOYEES.get(employee_id)
        if demo is not None:
            return {
                "employee_id": employee_id,
                "name": demo["name"],
                "email": demo["email"],
                "department": demo["department"],
                "manager_id": demo["manager_id"],
                "salary": None,
                "pending_salary": 0.0,
                "found": False,
            }
        return {
            "employee_id": employee_id,
            "name": "",
            "email": "",
            "department": "",
            "manager_id": None,
            "salary": None,
            "pending_salary": 0.0,
            "found": False,
        }
    finally:
        db.close()


class ListEmployeesInput(BaseModel):
    department: str = Field("", description="Optional department filter")


class ListEmployeesOutput(BaseModel):
    employees: list[dict]


def list_employees(department: str = "") -> dict:
    """List employees, optionally by department."""
    db = SessionLocal()
    try:
        query = db.query(Employee)
        if department:
            query = query.filter(Employee.department == department)
        rows = query.all()
        if rows:
            return {
                "employees": [
                    {
                        "employee_id": r.employee_id,
                        "name": r.name,
                        "email": r.email,
                        "department": r.department,
                        "manager_id": r.manager_id,
                    }
                    for r in rows
                ]
            }
    finally:
        db.close()
    emps = [
        {"employee_id": "E001", "name": "Alice", "department": "Engineering"},
        {"employee_id": "E002", "name": "Bob", "department": "HR"},
    ]
    if department:
        emps = [e for e in emps if e["department"] == department]
    return {"employees": emps}


TOOLS = [
    ToolSpec(
        name="get_employee_profile",
        description="Get all information related to an employee.",
        func=get_employee_profile,
        input_schema=EmployeeProfileInput,
        output_schema=EmployeeProfileOutput,
        requires_approval=False,
        risk_level="low",
        sensitive_fields=["employee_id", "email"],
        domain="employee",
    ),
    ToolSpec(
        name="list_employees",
        description="List employees, optionally by department.",
        func=list_employees,
        input_schema=ListEmployeesInput,
        output_schema=ListEmployeesOutput,
        requires_approval=False,
        risk_level="low",
        sensitive_fields=[],
        domain="employee",
    ),
]