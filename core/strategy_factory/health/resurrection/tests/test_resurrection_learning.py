from datetime import datetime, timedelta

import pytest

from core.strategy_factory.health.resurrection.learning import (
    ResurrectionLearningEngine,
    ResurrectionOutcomeArtifact,
)


# ======================================================
# Fixtures
# ======================================================

@pytest.fixture
def now():
    return datetime(2026, 1, 1, 12, 0, 0)


@pytest.fixture
def strategy_dna():
    return "test_dna_123"


# ======================================================
# Tests — Happy Path
# ======================================================

def test_allows_resurrection_with_no_failures(strategy_dna, now):
    outcomes = []

    signal = ResurrectionLearningEngine.evaluate(
        strategy_dna=strategy_dna,
        outcomes=outcomes,
        now=now,
    )

    assert signal.allowed is True
    assert signal.failure_count == 0
    assert signal.cooldown_until is None
    assert "allowed" in signal.reason.lower()


def test_allows_resurrection_with_single_failure(strategy_dna, now):
    outcomes = [
        ResurrectionOutcomeArtifact(
            dna=strategy_dna,
            success=False,
            timestamp=now - timedelta(days=10),
        )
    ]

    signal = ResurrectionLearningEngine.evaluate(
        strategy_dna=strategy_dna,
        outcomes=outcomes,
        now=now,
    )

    assert signal.allowed is True
    assert signal.failure_count == 1
    assert signal.cooldown_until is None


# ======================================================
# Tests — Cooldown Enforcement
# ======================================================

def test_blocks_resurrection_when_cooldown_active(strategy_dna, now):
    outcomes = [
        ResurrectionOutcomeArtifact(
            dna=strategy_dna,
            success=False,
            timestamp=now - timedelta(days=5),
        ),
        ResurrectionOutcomeArtifact(
            dna=strategy_dna,
            success=False,
            timestamp=now - timedelta(days=1),
        ),
    ]

    signal = ResurrectionLearningEngine.evaluate(
        strategy_dna=strategy_dna,
        outcomes=outcomes,
        now=now,
    )

    assert signal.allowed is False
    assert signal.failure_count == 2
    assert signal.cooldown_until is not None
    assert now < signal.cooldown_until
    assert "cooldown" in signal.reason.lower()


def test_allows_resurrection_after_cooldown_expires(strategy_dna, now):
    outcomes = [
        ResurrectionOutcomeArtifact(
            dna=strategy_dna,
            success=False,
            timestamp=now - timedelta(days=40),
        ),
        ResurrectionOutcomeArtifact(
            dna=strategy_dna,
            success=False,
            timestamp=now - timedelta(days=35),
        ),
    ]

    signal = ResurrectionLearningEngine.evaluate(
        strategy_dna=strategy_dna,
        outcomes=outcomes,
        now=now,
    )

    assert signal.allowed is True
    assert signal.failure_count == 2
    assert signal.cooldown_until is None


# ======================================================
# Tests — Filtering & Isolation
# ======================================================

def test_ignores_outcomes_from_other_strategies(strategy_dna, now):
    outcomes = [
        ResurrectionOutcomeArtifact(
            dna="other_dna",
            success=False,
            timestamp=now - timedelta(days=1),
        )
    ]

    signal = ResurrectionLearningEngine.evaluate(
        strategy_dna=strategy_dna,
        outcomes=outcomes,
        now=now,
    )

    assert signal.allowed is True
    assert signal.failure_count == 0


from datetime import datetime, timedelta

import pytest

from core.strategy_factory.health.resurrection.learning import (
    ResurrectionLearningStore,
)
from core.strategy_factory.health.resurrection.enums import OutcomeState


def test_learning_records_outcome():
    store = ResurrectionLearningStore()

    dna = "strategy_dna_1"

    store.record_outcome(
        dna=dna,
        outcome=OutcomeState.SUCCESS,
        timestamp=datetime.utcnow(),
        notes="Recovered edge in new regime",
    )

    history = store.history(dna)

    assert len(history) == 1
    assert history[0].outcome == OutcomeState.SUCCESS
    assert history[0].notes == "Recovered edge in new regime"


def test_learning_is_deterministic():
    store = ResurrectionLearningStore()
    dna = "strategy_dna_2"

    ts = datetime.utcnow()

    store.record_outcome(dna, OutcomeState.FAILURE, ts, notes=None)
    store.record_outcome(dna, OutcomeState.FAILURE, ts, notes=None)

    history = store.history(dna)

    # Deterministic: exact duplicates allowed but preserved
    assert len(history) == 2
    assert history[0].timestamp == history[1].timestamp
