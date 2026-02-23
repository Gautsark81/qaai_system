# core/bootstrap/tests/test_boot_time_enforce.py
import pytest
from core.execution.guards import register_kill_switch, assert_execution_allowed

class FakeKS:
    def __init__(self, armed=False):
        self._armed = armed
    def is_armed(self):
        return self._armed
    def is_tripped(self, scope=None):
        return False

def test_boot_fails_when_armed():
    ks = FakeKS(armed=True)
    register_kill_switch(lambda: ks)
    with pytest.raises(RuntimeError):
        assert_execution_allowed(callsite="boot/test")
