import pytest
from datetime import datetime, timezone

from core.runtime.run_registry import RunRegistry
from core.runtime.run_context import RunContext


def test_phase_mismatch_is_blocked():
    registry = RunRegistry()

    ctx1 = RunContext(
        run_id="run-001",
        git_commit="abc123",
        phase_version="11",
        config_fingerprint="cfg",
        start_time=datetime.now(timezone.utc),
    )

    ctx2 = RunContext(
        run_id="run-001",
        git_commit="abc123",
        phase_version="12",
        config_fingerprint="cfg",
        start_time=datetime.now(timezone.utc),
    )

    registry.register(ctx1)

    with pytest.raises(RuntimeError):
        registry.resume(ctx2)
