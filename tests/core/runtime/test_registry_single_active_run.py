import pytest
from datetime import datetime, timezone

from core.runtime.run_registry import RunRegistry
from core.runtime.run_context import RunContext


def _ctx(run_id):
    return RunContext(
        run_id=run_id,
        git_commit="abc123",
        phase_version="12",
        config_fingerprint="cfg",
        start_time=datetime.now(timezone.utc),
    )


def test_cannot_register_same_run_twice():
    registry = RunRegistry()
    ctx = _ctx("run-001")

    registry.register(ctx)

    with pytest.raises(RuntimeError):
        registry.register(ctx)
