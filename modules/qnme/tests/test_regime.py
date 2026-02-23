# modules/qnme/tests/test_regime.py
from modules.qnme.regime import RegimeEngine

def test_regime_rule_based():
    engine = RegimeEngine()
    # low volume, low entropy
    genome = {"genome": {"entropy": 0.2, "volume": 100.0, "imbalance": 0.0}}
    label, conf = engine.predict(genome)
    assert isinstance(label, str)
    assert conf >= 0.0
