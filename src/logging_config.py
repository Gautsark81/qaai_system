# Path: src/logging_config.py
"""Central logging configuration (call early in process start)."""
import logging
import sys

def configure_logging(level: str = "INFO"):
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s %(levelname)s %(name)s [%(threadName)s]: %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
