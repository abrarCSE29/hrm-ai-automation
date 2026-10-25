"""SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(256))
    department: Mapped[str] = mapped_column(String(128), default="")
    manager_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), default="anonymous")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    approval_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    trace_id: Mapped[str] = mapped_column(String(64), index=True)
    conversation_id: Mapped[str] = mapped_column(String(64), default="")
    agent_name: Mapped[str] = mapped_column(String(128), default="")
    tool_name: Mapped[str] = mapped_column(String(128))
    args: Mapped[dict] = mapped_column(JSON, default=dict)
    reasoning: Mapped[str] = mapped_column(Text, default="")
    risk_level: Mapped[str] = mapped_column(String(32), default="low")
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending/approved/rejected
    decision_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    trace_id: Mapped[str] = mapped_column(String(64), index=True)
    conversation_id: Mapped[str] = mapped_column(String(64), default="")
    agent_name: Mapped[str] = mapped_column(String(128), default="")
    user_input: Mapped[str] = mapped_column(Text, default="")
    tool_called: Mapped[str] = mapped_column(String(128), default="")
    tool_args: Mapped[dict] = mapped_column(JSON, default=dict)
    policy_decision: Mapped[str] = mapped_column(String(32), default="")
    approval_decision: Mapped[str] = mapped_column(String(32), default="")
    final_outcome: Mapped[str] = mapped_column(String(64), default="")
