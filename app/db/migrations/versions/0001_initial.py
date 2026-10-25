"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-25 12:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=256), nullable=False),
        sa.Column("department", sa.String(length=128), nullable=True),
        sa.Column("manager_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("conversation_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("user_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "approvals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("approval_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("conversation_id", sa.String(length=64), nullable=True),
        sa.Column("agent_name", sa.String(length=128), nullable=True),
        sa.Column("tool_name", sa.String(length=128), nullable=False),
        sa.Column("args", sa.JSON(), nullable=True),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=True),
        sa.Column("decision_note", sa.Text(), nullable=True),
        sa.Column("decided_by", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("trace_id", sa.String(length=64), nullable=False),
        sa.Column("conversation_id", sa.String(length=64), nullable=True),
        sa.Column("agent_name", sa.String(length=128), nullable=True),
        sa.Column("user_input", sa.Text(), nullable=True),
        sa.Column("tool_called", sa.String(length=128), nullable=True),
        sa.Column("tool_args", sa.JSON(), nullable=True),
        sa.Column("policy_decision", sa.String(length=32), nullable=True),
        sa.Column("approval_decision", sa.String(length=32), nullable=True),
        sa.Column("final_outcome", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_approvals_trace_id", "approvals", ["trace_id"])
    op.create_index("ix_audit_log_trace_id", "audit_log", ["trace_id"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("approvals")
    op.drop_table("conversations")
    op.drop_table("employees")
