# utils/logging.py
"""
Structured JSON logging using Python's logging module.
- All logs include IST timestamp (field 'ts_ist')
- Optional capture_stdout to route stdout prints through logger (useful in tests)
- Lightweight: no external JSON logger package required
"""

import logging
import json
import sys
from typing import Optional
from .ist_time import now_ist, format_iso_ist


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "ts_ist": format_iso_ist(now_ist()),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # include extra keys if provided (record.__dict__)
        extra = {k: v for k, v in record.__dict__.items() if k not in ("msg", "args", "levelname", "levelno", "name", "exc_info", "stack_info", "lineno", "funcName", "filename", "module", "pathname")}
        if extra:
            # try to make sure extras are JSON-serializable
            try:
                json.dumps(extra)
                base["extra"] = extra
            except Exception:
                base["extra"] = str(extra)
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(base, default=str)


def get_logger(name: str = "app", level: Optional[str] = None, capture_stdout: Optional[bool] = None) -> logging.Logger:
    level = level or (logging.getLevelName(logging.INFO) if isinstance(logging.getLevelName(logging.INFO), str) else "INFO")
    logger = logging.getLogger(name)
    if logger.handlers:
        # assume already configured
        return logger

    # Basic stream handler to stdout (so CI captures it)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.getLevelName(level) if isinstance(level, str) else level)

    # Optionally capture stdout (redirect print -> logger.info)
    cfg_capture = True if capture_stdout is None else bool(capture_stdout)
    if cfg_capture:
        class StdOutProxy:
            def write(self, s):
                s = s.strip()
                if s:
                    logger.info(s)

            def flush(self):
                pass
        sys.stdout = StdOutProxy()

    return logger
