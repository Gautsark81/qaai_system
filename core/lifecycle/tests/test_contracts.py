import pytest
from datetime import datetime

from core.lifecycle.contracts.state import LifecycleState
from core.lifecycle.contracts.enums import TransitionReason
from core.lifecycle.contracts.snapshot import LifecycleSnapshot


def test_lifecycle_states_exist():
    assert LifecycleState.LIVE.value == "LIVE"
    assert LifecycleState.RETIRED.value == "RETIRED"


def test_transition_reasons_exist():
    assert TransitionReason.SSR_STRONG.value == "SSR_STRONG"
    assert TransitionReason.OPERATOR_OVERRIDE.value == "OPERATOR_OVERRIDE"


def test_lifecycle_snapshot_frozen():
    snap = LifecycleSnapshot(
        strategy_id="s1",
        state=LifecycleState.PAPER,
        since=datetime.utcnow(),
        version="v1",
    )

    with pytest.raises(Exception):
        snap.state = LifecycleState.LIVE
