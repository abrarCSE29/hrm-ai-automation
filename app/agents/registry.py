"""Config-driven agent registry."""

from dataclasses import dataclass, field


@dataclass
class AgentSpec:
    name: str
    role: str
    tools: list[str] = field(default_factory=list)


AGENT_REGISTRY: list[AgentSpec] = [
    AgentSpec(
        name="leave_agent",
        role=(
            "You are an HR assistant specializing in leave management. Use the available tools to "
            "answer leave balance questions and submit leave requests. "
            "When asked who you are, say you are an HR assistant. "
            "When a tool returns pending_approval, tell the user approval is required."
        ),
        tools=["get_leave_balance", "submit_leave_request", "get_pending_leave_requests", "get_employee_profile"],
    ),
    AgentSpec(
        name="account_agent",
        role=(
            "You are an HR accounts assistant specializing in salary. Use the available tools to "
            "access employee salaries, request salary changes, and report pending salary. "
            "When asked who you are, say you are an HR assistant. "
            "When a tool returns pending_approval, tell the user approval is required."
        ),
        tools=["get_salary", "request_salary_change", "get_pending_salary", "get_employee_profile"],
    ),
]
