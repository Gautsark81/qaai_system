import pytest
from core.execution.execution_guard import ExecutionGuard


def test_execution_guard_blocks_resurrection(record):
    record.state = "RESURRECTION_CANDIDATE"

    with pytest.raises(PermissionError):
        ExecutionGuard.assert_can_execute(record)
