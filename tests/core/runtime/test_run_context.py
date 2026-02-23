import pytest
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

from core.runtime.run_context import RunContext


def test_run_context_is_immutable():
    ctx = RunContext(
        run_id="run-001",
        git_commit="abc123",
        phase_version="12",
        config_fingerprint="cfg-hash",
        start_time=datetime.now(timezone.utc),
    )

    with pytest.raises(FrozenInstanceError):
        ctx.run_id = "run-002"


def test_run_context_requires_all_fields():
    with pytest.raises(TypeError):
        RunContext(run_id="run-001")  # missing required fields
