import pytest
from core.runtime.production_guard import ProductionGuard
from core.runtime.release_lock import ReleaseLock
from core.lifecycle.contracts.state import LifecycleState


class DummyAuthorizer:
    """Minimal stub — do NOT inherit SystemAuthorizer"""

    def authorize(self, *, lifecycle_state, execution_guard_armed):
        class Result:
            allowed = True
            reason = "OK"

        return Result()


def test_production_guard_blocks_without_live_env(tmp_path):
    lock = ReleaseLock(tmp_path, expected_hash="dummy")

    guard = ProductionGuard(
        env="PAPER",  # NOT LIVE
        release_lock=lock,
        authorizer=DummyAuthorizer(),
        execution_guard_armed=True,
    )

    with pytest.raises(RuntimeError):
        guard.authorize_or_raise(LifecycleState.LIVE)
