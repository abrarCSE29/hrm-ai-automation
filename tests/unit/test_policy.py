from app.policy import PolicyEngine, default_rules


def test_policy_allows_small_leave():
    engine = PolicyEngine(default_rules())
    d = engine.validate("submit_leave_request", {"employee_id": "E1", "days": 3})
    assert d.allowed is True
    assert d.reasons == []


def test_policy_blocks_long_leave():
    engine = PolicyEngine(default_rules())
    d = engine.validate("submit_leave_request", {"employee_id": "E1", "days": 10})
    assert d.allowed is False
    assert any("manager approval" in r for r in d.reasons)


def test_policy_blocks_invalid_days():
    engine = PolicyEngine(default_rules())
    d = engine.validate("submit_leave_request", {"employee_id": "E1", "days": 0})
    assert d.allowed is False


def test_policy_ignores_other_actions():
    engine = PolicyEngine(default_rules())
    d = engine.validate("get_leave_balance", {"employee_id": "E1"})
    assert d.allowed is True
