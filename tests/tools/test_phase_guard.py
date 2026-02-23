import pytest
from tools.phase_guard.phase_guard import enforce_phase_guard


def test_phase_guard_runs():
    # Should not raise when no illegal diffs exist
    enforce_phase_guard(base="HEAD")
