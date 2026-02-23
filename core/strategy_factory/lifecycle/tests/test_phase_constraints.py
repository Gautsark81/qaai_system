import pytest
from core.strategy_factory.lifecycle.phase_constraints import assert_execution_allowed
from core.strategy_factory.exceptions import ExecutionNotAllowed


def test_phase_b_blocks_execution():
    with pytest.raises(ExecutionNotAllowed):
        assert_execution_allowed(phase="PHASE_B")
