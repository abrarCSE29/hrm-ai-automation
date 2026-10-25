from agno.models.response import ModelResponse

from app.agents.mock_model import MockModel
from app.orchestrator.supervisor import run_chat


def test_supervisor_routes_leave_balance():
    model = MockModel(
        responses=[
            ModelResponse(
                tool_calls=[
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {
                            "name": "delegate_task_to_member",
                            "arguments": '{"member_id": "leave-agent", "task": "What is my leave balance?"}',
                        },
                    }
                ]
            ),
            ModelResponse(
                tool_calls=[
                    {
                        "id": "c2",
                        "type": "function",
                        "function": {
                            "name": "get_leave_balance",
                            "arguments": '{"employee_id": "E001"}',
                        },
                    }
                ]
            ),
            ModelResponse(content="Your annual leave balance is 12 days."),
        ]
    )
    result = run_chat("What is my leave balance?", model=model)
    assert "12" in result or "balance" in result.lower()
