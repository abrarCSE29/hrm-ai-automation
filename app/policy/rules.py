"""Example policy rules (plain Python)."""

from app.policy.engine import PolicyRule


class LeaveDaysPositiveRule:
    """Leave days must be positive and within a sane maximum."""

    def evaluate(self, action: str, args: dict) -> str | None:
        if action != "submit_leave_request":
            return None
        days = args.get("days")
        if days is None:
            return None
        if not isinstance(days, int) or days < 1:
            return "leave days must be a positive integer"
        if days > 30:
            return "leave days cannot exceed 30"
        return None


class LongLeaveRequiresManagerApprovalRule:
    """Leave requests longer than 5 days require manager approval (blocked here)."""

    def evaluate(self, action: str, args: dict) -> str | None:
        if action != "submit_leave_request":
            return None
        days = args.get("days")
        if isinstance(days, int) and days > 5:
            return "leave requests over 5 days require manager approval"
        return None


def default_rules() -> list[PolicyRule]:
    return [LeaveDaysPositiveRule(), LongLeaveRequiresManagerApprovalRule()]
