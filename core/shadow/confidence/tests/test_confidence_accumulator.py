from core.shadow.confidence.accumulator import ShadowConfidenceAccumulator
from core.shadow.confidence.models import ShadowConfidenceState


def test_confidence_increases_with_low_divergence():
    acc = ShadowConfidenceAccumulator()
    state = ShadowConfidenceState(strategy_id="s1")

    snap1 = acc.update(state, divergence_score=0.1)
    snap2 = acc.update(state, divergence_score=0.05)

    assert snap2.confidence > snap1.confidence
    assert snap2.confidence > 0.0


def test_confidence_decays_with_high_divergence():
    acc = ShadowConfidenceAccumulator()
    state = ShadowConfidenceState(strategy_id="s1", confidence=0.5, observations=10)

    snap = acc.update(state, divergence_score=1.0)

    assert snap.confidence < 0.5


def test_confidence_clamped_to_bounds():
    acc = ShadowConfidenceAccumulator()
    state = ShadowConfidenceState(strategy_id="s1", confidence=0.99, observations=50)

    snap = acc.update(state, divergence_score=0.0)
    assert snap.confidence <= 1.0

    state.confidence = 0.01
    snap = acc.update(state, divergence_score=5.0)
    assert snap.confidence >= 0.0


def test_more_observations_increase_inertia():
    acc = ShadowConfidenceAccumulator(gain_rate=0.1)
    early = ShadowConfidenceState(strategy_id="s1", observations=1)
    late = ShadowConfidenceState(strategy_id="s1", observations=50)

    snap_early = acc.update(early, divergence_score=0.0)
    snap_late = acc.update(late, divergence_score=0.0)

    assert snap_early.confidence > snap_late.confidence
