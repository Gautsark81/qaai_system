import pytest

from core.strategy_factory.lifecycle.contracts import (
    StrategyLifecycleState,
    is_transition_allowed,
)

# ======================================================
# 🔁 EXISTING GOVERNANCE TESTS (UNCHANGED)
# ======================================================

@pytest.mark.parametrize(
    "src,dst",
    [
        (StrategyLifecycleState.RESEARCH, StrategyLifecycleState.BACKTESTED),
        (StrategyLifecycleState.BACKTESTED, StrategyLifecycleState.PAPER),
        (StrategyLifecycleState.PAPER, StrategyLifecycleState.LIVE),
        (StrategyLifecycleState.LIVE, StrategyLifecycleState.DEGRADED),
        (StrategyLifecycleState.DEGRADED, StrategyLifecycleState.PAPER),
        (StrategyLifecycleState.DEGRADED, StrategyLifecycleState.RETIRED),
    ],
)
def test_allowed_transitions(src, dst):
    assert is_transition_allowed(src, dst) is True


@pytest.mark.parametrize(
    "src,dst",
    [
        (StrategyLifecycleState.RESEARCH, StrategyLifecycleState.LIVE),
        (StrategyLifecycleState.RESEARCH, StrategyLifecycleState.RETIRED),
        (StrategyLifecycleState.PAPER, StrategyLifecycleState.RESEARCH),
        (StrategyLifecycleState.LIVE, StrategyLifecycleState.PAPER),
        (StrategyLifecycleState.RETIRED, StrategyLifecycleState.LIVE),
    ],
)
def test_forbidden_transitions(src, dst):
    assert is_transition_allowed(src, dst) is False


def test_self_transition_is_forbidden():
    assert (
        is_transition_allowed(
            StrategyLifecycleState.LIVE,
            StrategyLifecycleState.LIVE,
        )
        is False
    )


def test_lifecycle_states_are_stable():
    states = [s.value for s in StrategyLifecycleState]
    assert states == [
        "RESEARCH",
        "BACKTESTED",
        "PAPER",
        "LIVE",
        "DEGRADED",
        "RETIRED",
    ]


# ======================================================
# 🧾 EVIDENCE EMISSION TESTS (ADDITIVE)
# ======================================================

from core.evidence.decision_store import DecisionEvidenceStore
from core.strategy_factory.lifecycle.evidence_emitter import (
    emit_lifecycle_transition_evidence,
)
from core.strategy_factory.lifecycle.evidence_contracts import (
    LifecycleTransitionEvidence,
)


def test_lifecycle_transition_emits_evidence():
    store = DecisionEvidenceStore()

    evidence = LifecycleTransitionEvidence(
        strategy_id="alpha_1",
        from_state=StrategyLifecycleState.RESEARCH,
        to_state=StrategyLifecycleState.BACKTESTED,
        reason="Backtest completed",
        transition_id="T-001",
    )

    emit_lifecycle_transition_evidence(
        evidence=evidence,
        store=store,
    )

    records = store.all()
    assert len(records) == 1

    record = records[0]
    assert record.decision_type == "LIFECYCLE_TRANSITION"
    assert record.strategy_id == "alpha_1"
    assert ("from_state", "RESEARCH") in record.factors
    assert ("to_state", "BACKTESTED") in record.factors


def test_lifecycle_transition_evidence_is_deterministic():
    store_1 = DecisionEvidenceStore()
    store_2 = DecisionEvidenceStore()

    evidence = LifecycleTransitionEvidence(
        strategy_id="alpha_2",
        from_state=StrategyLifecycleState.PAPER,
        to_state=StrategyLifecycleState.LIVE,
        reason="Promotion approved",
        transition_id="T-XYZ",
    )

    emit_lifecycle_transition_evidence(evidence=evidence, store=store_1)
    emit_lifecycle_transition_evidence(evidence=evidence, store=store_2)

    r1 = store_1.all()[0]
    r2 = store_2.all()[0]

    assert r1.checksum == r2.checksum
    assert r1.factors == r2.factors


def test_lifecycle_evidence_does_not_mutate_states():
    src = StrategyLifecycleState.RESEARCH
    dst = StrategyLifecycleState.BACKTESTED

    store = DecisionEvidenceStore()

    evidence = LifecycleTransitionEvidence(
        strategy_id="alpha_3",
        from_state=src,
        to_state=dst,
        reason=None,
        transition_id="IMMUTABLE",
    )

    emit_lifecycle_transition_evidence(evidence=evidence, store=store)

    # Original enum values remain unchanged
    assert src == StrategyLifecycleState.RESEARCH
    assert dst == StrategyLifecycleState.BACKTESTED
