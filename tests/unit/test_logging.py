# tests/unit/test_logging.py
import sys
import logging
from utils.logging import get_logger
import json
import re
import io

def test_logger_outputs_json(capsys):
    # get a logger and write a message
    logger = get_logger("test_logger_for_phase0", level="INFO", capture_stdout=False)
    logger.info("hello world")
    captured = capsys.readouterr()
    # logger writes JSON to stdout; parse lines
    lines = [l for l in captured.out.splitlines() if l.strip()]
    assert lines, f"no log output captured: {captured.out!r}"
    # parse last line as json
    data = json.loads(lines[-1])
    assert data["level"] == "INFO"
    assert "hello world" in data["message"]

def test_logger_capture_stdout(monkeypatch, capsys):
    # create a new logger that captures stdout (we reset sys.stdout in module)
    logger = get_logger("test_capture_stdout", level="INFO", capture_stdout=True)
    print("printed via stdout")
    captured = capsys.readouterr()
    lines = [l for l in captured.out.splitlines() if l.strip()]
    # last line is the JSON version of "printed via stdout"
    assert any("printed via stdout" in l for l in lines)
