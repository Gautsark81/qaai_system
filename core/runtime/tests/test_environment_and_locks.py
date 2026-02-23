import pytest
from core.runtime.environment import RuntimeEnvironment
from core.runtime.execution_lock import ExecutionLock


def test_invalid_env_blocks():
    with pytest.raises(ValueError):
        RuntimeEnvironment("unknown", allow_live_execution=False)


def test_live_blocked_in_staging():
    env = RuntimeEnvironment("staging", allow_live_execution=False)
    lock = ExecutionLock(env, armed=True)
    assert lock.can_execute_live() is False


def test_live_requires_prod_and_armed():
    env = RuntimeEnvironment("prod", allow_live_execution=True)

    assert ExecutionLock(env, armed=False).can_execute_live() is False
    assert ExecutionLock(env, armed=True).can_execute_live() is True
