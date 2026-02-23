from core.strategy_factory.health.decay.decay_engine import AlphaDecayDetector
from core.strategy_factory.health.decay.decay_state import AlphaDecayState


def test_decay_state_classification():
    d = AlphaDecayDetector()

    assert d._classify(0.2) == AlphaDecayState.HEALTHY
    assert d._classify(0.4) == AlphaDecayState.WARNING
    assert d._classify(0.6) == AlphaDecayState.DEGRADING
    assert d._classify(0.9) == AlphaDecayState.CRITICAL
