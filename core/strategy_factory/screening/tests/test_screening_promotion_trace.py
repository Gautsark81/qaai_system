# core/strategy_factory/screening/tests/test_screening_promotion_trace.py

from core.strategy_factory.screening.screening_promotion_trace import (
    build_screening_promotion_trace,
)


def test_trace_is_deterministic():
    trace1 = build_screening_promotion_trace(
        screening_state_hash="abc",
        advisory_state_hash="def",
        policy_params=("SSR=0.8", "REGIME=BULL"),
    )

    trace2 = build_screening_promotion_trace(
        screening_state_hash="abc",
        advisory_state_hash="def",
        policy_params=("REGIME=BULL", "SSR=0.8"),  # different order
    )

    assert trace1.trace_hash == trace2.trace_hash


def test_trace_changes_if_screening_changes():
    t1 = build_screening_promotion_trace(
        screening_state_hash="A",
        advisory_state_hash="B",
        policy_params=("X",),
    )

    t2 = build_screening_promotion_trace(
        screening_state_hash="Z",
        advisory_state_hash="B",
        policy_params=("X",),
    )

    assert t1.trace_hash != t2.trace_hash


def test_trace_changes_if_advisory_changes():
    t1 = build_screening_promotion_trace(
        screening_state_hash="A",
        advisory_state_hash="B",
        policy_params=("X",),
    )

    t2 = build_screening_promotion_trace(
        screening_state_hash="A",
        advisory_state_hash="C",
        policy_params=("X",),
    )

    assert t1.trace_hash != t2.trace_hash


def test_trace_changes_if_policy_changes():
    t1 = build_screening_promotion_trace(
        screening_state_hash="A",
        advisory_state_hash="B",
        policy_params=("X",),
    )

    t2 = build_screening_promotion_trace(
        screening_state_hash="A",
        advisory_state_hash="B",
        policy_params=("Y",),
    )

    assert t1.trace_hash != t2.trace_hash