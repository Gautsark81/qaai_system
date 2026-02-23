import pytest
from core.logging_utils.structured_logger import StructuredLogger


def test_logger_requires_run_id():
    with pytest.raises(ValueError):
        StructuredLogger(run_id="", stream=None, jsonl_path=None)
