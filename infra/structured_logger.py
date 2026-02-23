from __future__ import annotations

"""
Structured logging helpers.

Goal:
- Provide a simple, safe way to emit JSON-like structured logs
  without forcing the whole codebase to use a custom logger class.

Usage:
    from infra.structured_logger import log_structured

    log_structured(logger, "INFO", "TRADING_CYCLE",
                   mode="paper",
                   cycle_latency_ms=42.0,
                   num_signals=3)

This will emit a single log line where the message is a JSON string
with at least an "event" field, plus any extra fields passed in.
"""

import json
import logging
import time
import uuid
from typing import Any, Dict, Optional


def make_structured_record(
    event: str,
    level: str = "INFO",
    correlation_id: Optional[str] = None,
    **fields: Any,
) -> Dict[str, Any]:
    """
    Build a structured record (dict) for logging.

    We do not enforce any schema other than:
        - event (str)
        - level (str)
        - ts (float unix timestamp)
        - correlation_id (optional)
    """
    record: Dict[str, Any] = {
        "event": event,
        "level": level.upper(),
        "ts": time.time(),
    }
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    record["correlation_id"] = correlation_id

    # Merge extra fields (best-effort JSON-serializable)
    for k, v in fields.items():
        try:
            json.dumps(v)  # probe serializability
            record[k] = v
        except TypeError:
            # Fallback to repr for non-serializable values
            record[k] = repr(v)

    return record


def log_structured(
    logger: logging.Logger,
    level: str,
    event: str,
    correlation_id: Optional[str] = None,
    **fields: Any,
) -> None:
    """
    Emit a structured log line via the given logger.

    We keep this deliberately simple:
      - Build a record dict
      - Dump to JSON string
      - Call logger.log(levelno, json_str)

    Any errors in building/dumping are swallowed; logging is best-effort.
    """
    try:
        record = make_structured_record(
            event=event,
            level=level,
            correlation_id=correlation_id,
            **fields,
        )
        msg = json.dumps(record, separators=(",", ":"))
        levelno = getattr(logging, level.upper(), logging.INFO)
        logger.log(levelno, msg)
    except Exception:
        # Absolutely never let logging crash the app
        try:
            logger.warning("structured_log_failed event=%s fields=%s", event, fields)
        except Exception:
            pass
