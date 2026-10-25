from app.tools.registry import ToolRegistry, registry


def test_registry_discovers_tools():
    names = registry.names()
    assert "get_leave_balance" in names
    assert "submit_leave_request" in names
    assert "get_employee_profile" in names


def test_registry_get_and_specs():
    reg = ToolRegistry()
    reg.discover()
    spec = reg.get("get_leave_balance")
    assert spec.domain == "leave"
    assert spec.requires_approval is False
    assert reg.specs_for(["get_leave_balance"])[0].name == "get_leave_balance"


def test_registry_redact():
    reg = ToolRegistry()
    reg.discover()
    redacted = reg.redact("submit_leave_request", {"employee_id": "E1", "days": 5})
    assert redacted["employee_id"] == "[REDACTED]"
    assert redacted["days"] == 5
