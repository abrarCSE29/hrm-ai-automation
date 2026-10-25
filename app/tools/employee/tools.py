"""Employee tools (framework-agnostic)."""

from pydantic import BaseModel, Field

from app.tools.base import ToolSpec


class EmployeeProfileInput(BaseModel):
    employee_id: str = Field(..., description="Employee identifier")


class EmployeeProfileOutput(BaseModel):
    employee_id: str
    name: str
    department: str
    manager_id: str | None


def get_employee_profile(employee_id: str) -> dict:
    """Return a demo employee profile."""
    return {
        "employee_id": employee_id,
        "name": "Demo Employee",
        "department": "Engineering",
        "manager_id": "MGR-001",
    }


class ListEmployeesInput(BaseModel):
    department: str = Field("", description="Optional department filter")


class ListEmployeesOutput(BaseModel):
    employees: list[dict]


def list_employees(department: str = "") -> dict:
    """List demo employees, optionally filtered by department."""
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
        description="Get an employee's profile.",
        func=get_employee_profile,
        input_schema=EmployeeProfileInput,
        output_schema=EmployeeProfileOutput,
        requires_approval=False,
        risk_level="low",
        sensitive_fields=["employee_id"],
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
