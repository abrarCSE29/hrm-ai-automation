"""Request tracing: trace IDs propagated via contextvars."""

import uuid
from contextvars import ContextVar

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
conversation_id_var: ContextVar[str] = ContextVar("conversation_id", default="")
user_input_var: ContextVar[str] = ContextVar("user_input", default="")


def new_trace_id() -> str:
    return uuid.uuid4().hex


def set_trace_context(trace_id: str, conversation_id: str = "", user_input: str = "") -> None:
    trace_id_var.set(trace_id)
    conversation_id_var.set(conversation_id)
    user_input_var.set(user_input)


def get_trace_id() -> str:
    return trace_id_var.get() or ""


def get_conversation_id() -> str:
    return conversation_id_var.get() or ""


def get_user_input() -> str:
    return user_input_var.get() or ""
