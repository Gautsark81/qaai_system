from datetime import datetime, timedelta

import pytest

from core.strategy_factory.health.resurrection.suppression import (
    ResurrectionSuppressionEngine,
)
from core.strategy_factory.health.resurrection.enums import (
    OutcomeState,
    SuppressionState,
)


def test_suppression_triggers_after_repeated_failures():
    engine = ResurrectionSuppressionEngine(
        failure_threshold=2,
        cooldown_period=timedelta(days=30),
    )

    dna = "strategy_dna_fail"

    engine.record_outcome(dna, OutcomeState.FAILURE)
    engine.record_outcome(dna, OutcomeState.FAILURE)

    assert engine.state(dna) == SuppressionState.SUPPRESSED


def test_suppression_blocks_resurrection_during_cooldown():
    now = datetime.utcnow()

    engine = ResurrectionSuppressionEngine(
        failure_threshold=1,
        cooldown_period=timedelta(days=10),
    )

    dna = "strategy_dna_cooldown"

    engine.record_outcome(
        dna,
        OutcomeState.FAILURE,
        timestamp=now,
    )

    # 5 days later → still suppressed
    assert (
        engine.is_allowed(
            dna,
            at_time=now + timedelta(days=5),
        )
        is False
    )

    # 15 days later → cooldown expired
    assert (
        engine.is_allowed(
            dna,
            at_time=now + timedelta(days=15),
        )
        is True
    )
