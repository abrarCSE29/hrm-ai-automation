"""Framework-agnostic tool execution with policy + approval + audit."""

import uuid

from app.approval.service import audit, create_pending_approval
from app.core.trace import get_conversation_id, get_trace_id, get_user_input
from app.db.session import SessionLocal
from app.policy import PolicyEngine, default_rules
from app.tools.base import ToolSpec


def execute_tool(spec: ToolSpec, args: dict, agent_name: str = "") -> dict:
    from app.core.observability import is_tracing_enabled, trace_run

    def _run() -> dict:
        db = SessionLocal()
        trace_id = get_trace_id() or uuid.uuid4().hex
        conversation_id = get_conversation_id()
        user_input = get_user_input()
        try:
            validated = spec.input_schema(**(args or {}))
            validated_args = validated.model_dump()
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "message": f"invalid args: {exc}"}

        engine = PolicyEngine(default_rules())
        decision = engine.validate(spec.name, validated_args)
        policy_decision = "allowed" if decision.allowed else "denied"

        if not decision.allowed:
            audit(
                db,
                trace_id=trace_id,
                conversation_id=conversation_id,
                agent_name=agent_name,
                user_input=user_input,
                tool_called=spec.name,
                tool_args=_redact(spec.name, validated_args),
                policy_decision=policy_decision,
                approval_decision="n/a",
                final_outcome="policy_denied",
            )
            return {"status": "policy_denied", "reasons": decision.reasons, "message": "; ".join(decision.reasons)}

        if spec.requires_approval:
            approval = create_pending_approval(
                db,
                tool_name=spec.name,
                args=validated_args,
                reasoning=f"Agent {agent_name} proposed {spec.name} with args {validated_args}",
                risk_level=spec.risk_level,
                agent_name=agent_name,
                trace_id=trace_id,
                conversation_id=conversation_id,
            )
            audit(
                db,
                trace_id=trace_id,
                conversation_id=conversation_id,
                agent_name=agent_name,
                user_input=user_input,
                tool_called=spec.name,
                tool_args=_redact(spec.name, validated_args),
                policy_decision=policy_decision,
                approval_decision="pending",
                final_outcome="pending_approval",
            )
            return {
                "status": "pending_approval",
                "approval_id": approval.approval_id,
                "message": f"Approval required before executing {spec.name}.",
            }

        try:
            result = spec.func(**validated_args)
            audit(
                db,
                trace_id=trace_id,
                conversation_id=conversation_id,
                agent_name=agent_name,
                user_input=user_input,
                tool_called=spec.name,
                tool_args=_redact(spec.name, validated_args),
                policy_decision=policy_decision,
                approval_decision="not_required",
                final_outcome="executed",
            )
            return {"status": "ok", "data": result}
        except Exception as exc:  # noqa: BLE001
            audit(
                db,
                trace_id=trace_id,
                conversation_id=conversation_id,
                agent_name=agent_name,
                user_input=user_input,
                tool_called=spec.name,
                tool_args=_redact(spec.name, validated_args),
                policy_decision=policy_decision,
                approval_decision="not_required",
                final_outcome=f"error: {exc}",
            )
            return {"status": "error", "message": str(exc)}

    if is_tracing_enabled():
        with trace_run(spec.name, run_type="tool", inputs=args or {}, metadata={"agent": agent_name, "domain": spec.domain}) as run:
            result = _run()
            if run is not None:
                run.outputs = result
            return result
    return _run()

def _redact(tool_name: str, args: dict) -> dict:
    from app.tools.registry import registry

    return registry.redact(tool_name, args)
