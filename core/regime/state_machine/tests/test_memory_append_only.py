from core.regime.state_machine.memory_ledger import RegimeMemoryLedger
from core.regime.state_machine.models import GlobalRegimeState


def test_append_only_behavior():
    ledger = RegimeMemoryLedger()

    state = GlobalRegimeState(
        regime_label="BULL",
        start_cycle=1,
        current_cycle=1,
        duration_cycles=1,
        age_bucket="early",
        transition_score=0.1,
        stability_score=0.9,
        structural_break_score=0.0,
        confidence_score=0.9,
    )

    ledger.append(state)
    history = ledger.history()

    assert len(history) == 1
    assert history[0] == state