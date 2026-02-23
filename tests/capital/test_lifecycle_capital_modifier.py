from core.capital.lifecycle.modifier import LifecycleCapitalModifier
from core.lifecycle.contracts.snapshot import LifecycleState


def test_lifecycle_multiplier_mapping():
    assert LifecycleCapitalModifier.multiplier_for(
        lifecycle_state=LifecycleState.CANDIDATE
    ) == 0.25

    assert LifecycleCapitalModifier.multiplier_for(
        lifecycle_state=LifecycleState.PAPER
    ) == 0.50

    assert LifecycleCapitalModifier.multiplier_for(
        lifecycle_state=LifecycleState.LIVE
    ) == 1.00


def test_unknown_state_fails_closed():
    class FakeState:
        pass

    assert LifecycleCapitalModifier.multiplier_for(
        lifecycle_state=FakeState()  # type: ignore
    ) == 0.0
