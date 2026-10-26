"""Accounts tools aggregator.

Each tool lives in its own module (``get_salary.py``, ``request_salary_change.py``,
``get_pending_salary.py``) and exports a module-level ``TOOLS`` list. This module
re-exports the combined list so the documented
``app.tools.<domain>.tools.TOOLS`` contract still holds.
"""

from app.tools.accounts.get_pending_salary import TOOLS as PENDING_SALARY_TOOLS
from app.tools.accounts.get_salary import TOOLS as SALARY_TOOLS
from app.tools.accounts.request_salary_change import TOOLS as SALARY_CHANGE_TOOLS
from app.tools.base import ToolSpec

TOOLS: list[ToolSpec] = [*SALARY_TOOLS, *SALARY_CHANGE_TOOLS, *PENDING_SALARY_TOOLS]

__all__ = ["TOOLS"]
