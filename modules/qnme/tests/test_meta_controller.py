# modules/qnme/tests/test_meta_controller.py
from modules.qnme.meta_controller import MetaController
from modules.strategy.base import Signal

def test_meta_aggregate_smoothing():
    mc = MetaController(smoothing_tau=2.0)
    sigs = [{"strategy_id": "s1", "signal": Signal("s1","FOO","BUY",1), "confidence": 0.8}]
    weights = mc.aggregate(sigs, ("low_vol_range", 0.6))
    assert "s1" in weights
    # second call should smooth from previous
    weights2 = mc.aggregate(sigs, ("low_vol_range", 0.6))
    assert weights2["s1"] == mc.last_weights["s1"]
