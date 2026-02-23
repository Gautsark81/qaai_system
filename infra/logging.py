# infra/logging.py
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


class JsonFormatter(logging.Formatter):
    """Simple JSON formatter with IST timestamp."""

    def format(self, record: logging.LogRecord) -> str:
        base: Dict[str, Any] = {
            "ts": datetime.now(IST).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Extra fields (if any)
        for key, value in record.__dict__.items():
            if key in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }:
                continue
            base[key] = value

        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(base, ensure_ascii=False)


def _ensure_root_logger(level: int, json_logs: bool) -> None:
    root = logging.getLogger()
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    if json_logs:
        handler.setFormatter(JsonFormatter())
    else:
        fmt = (
            "%(asctime)s | %(levelname)s | %(name)s | "
            "%(funcName)s:%(lineno)d | %(message)s"
        )
        handler.setFormatter(logging.Formatter(fmt))

    root.addHandler(handler)
    root.setLevel(level)


def configure_logging(
    level: int = logging.INFO, *, json_logs: bool = True
) -> None:
    """
    Configure root logger.

    Call once during app bootstrap (e.g. in main_orchestrator.py).
    """
    _ensure_root_logger(level, json_logs)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a logger that is guaranteed to have a handler.
    """
    _ensure_root_logger(logging.INFO, json_logs=True)
    return logging.getLogger(name)
