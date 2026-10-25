"""Optional LangSmith observability helpers."""

import os
from contextlib import contextmanager
from typing import Any

from app.core.config import settings


def _sync_env() -> None:
    if settings.LANGSMITH_API_KEY:
        os.environ.setdefault("LANGSMITH_API_KEY", settings.LANGSMITH_API_KEY)
    if settings.LANGSMITH_PROJECT:
        os.environ.setdefault("LANGSMITH_PROJECT", settings.LANGSMITH_PROJECT)
    if settings.LANGSMITH_ENDPOINT:
        os.environ.setdefault("LANGSMITH_ENDPOINT", settings.LANGSMITH_ENDPOINT)
    if settings.LANGSMITH_TRACING or settings.LANGCHAIN_TRACING_V2:
        os.environ.setdefault("LANGSMITH_TRACING", "true")


_sync_env()


def is_tracing_enabled() -> bool:
    flag = settings.LANGSMITH_TRACING or settings.LANGCHAIN_TRACING_V2
    env_flag = os.getenv("LANGSMITH_TRACING", "").lower() in ("1", "true", "yes", "on") or os.getenv(
        "LANGCHAIN_TRACING_V2", ""
    ).lower() in ("1", "true", "yes", "on")
    has_key = bool(settings.LANGSMITH_API_KEY or os.getenv("LANGSMITH_API_KEY"))
    return (flag or env_flag) and has_key


@contextmanager
def trace_run(name: str, run_type: str = "chain", *, inputs: dict | None = None, metadata: dict | None = None, tags=None, project_name: str | None = None):
    if not is_tracing_enabled():
        yield None
        return
    from langsmith.run_helpers import trace

    project = project_name or settings.LANGSMITH_PROJECT
    with trace(
        name,
        run_type=run_type,
        inputs=inputs or {},
        metadata=metadata or {},
        tags=tags or [],
        project_name=project,
    ) as run:
        yield run


def record_usage(run: Any, usage: dict, model_name: str, provider: str) -> None:
    if run is None:
        return
    try:
        run.extra = run.extra or {}
        run.extra.setdefault("usage_metadata", usage)
        run.metadata = run.metadata or {}
        run.metadata.update({"ls_provider": provider, "ls_model_name": model_name})
    except Exception:  # noqa: BLE001, S110
        pass
