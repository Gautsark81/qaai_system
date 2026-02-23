# core/execution/tests/test_execution_kill_switch_guard.py
import pytest

from core.execution.guards import register_kill_switch, assert_execution_allowed

class FakeKS:
    def __init__(self, armed=False, tripped=False):
        self._armed = armed
        self._tripped = tripped
    def is_armed(self):
        return self._armed
    def is_tripped(self, scope=None):
        return self._tripped

def test_allows_when_not_armed():
    ks = FakeKS(armed=False, tripped=False)
    register_kill_switch(lambda: ks)
    assert_execution_allowed()  # should not raise

def test_blocks_when_armed():
    ks = FakeKS(armed=True, tripped=False)
    register_kill_switch(lambda: ks)
    with pytest.raises(RuntimeError):
        assert_execution_allowed()

def test_blocks_when_tripped():
    ks = FakeKS(armed=False, tripped=True)
    register_kill_switch(lambda: ks)
    with pytest.raises(RuntimeError):
        assert_execution_allowed()
