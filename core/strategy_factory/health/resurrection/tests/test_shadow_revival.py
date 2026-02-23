import pytest
from core.execution.execution_guard import ExecutionGuard


def test_shadow_has_no_execution_access(record):
    record.state = "REVIVAL_SHADOW"

    with pytest.raises(PermissionError):
        ExecutionGuard.assert_can_execute(record)
