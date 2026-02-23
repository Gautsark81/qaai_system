# modules/qnme/tests/test_gates.py
from modules.qnme.gates import GatePipeline
from modules.strategy.base import Signal

def test_gate_pipeline_allows_simple():
    gp = GatePipeline()
    candidate = {"signal": Signal(strategy_id="s1", symbol="FOO", side="BUY", size=1.0)}
    tick = {"price": 100.0, "spread": 0.001}
    genome = {"genome": {"avg_dt": 10, "liquidity_p_large": 0.1, "imbalance": 0}}
    ok, details = gp.validate(candidate, tick, genome, ("low_vol_range", 0.7))
    assert ok
