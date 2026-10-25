"""Structured logging helpers."""

import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | trace=%(trace_id)s | %(message)s",
        stream=sys.stdout,
    )
    # ensure trace_id filter default
    for handler in logging.root.handlers:
        handler.addFilter(_TraceFilter())


class _TraceFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "trace_id"):
            record.trace_id = "-"
        return True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
