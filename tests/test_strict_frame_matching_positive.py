import pandas as pd
from modules.strategy.strategy_factory import StrategyFactory
from modules.feature_engine.fusion_engine import FusionEngine

def test_strict_frame_matching_resolves():
    f1 = pd.DataFrame({"timestamp": [1, 2], "signal": [1, 2]})
    f2 = pd.DataFrame({"timestamp": [1, 2], "signal": [2, 4]})
    fused = FusionEngine({"mode": "join", "on": "timestamp"}).fuse({"x": f1, "y": f2})

    cfg = {
        "frame_resolution": "strict",
        "rules": {
            "r": {"op": ">", "col": "x.signal", "val": 1.5}
        },
        "signals": {
            "buy": {"rule": "r", "value": 1}
        }
    }
    sf = StrategyFactory(cfg)
    out = sf.generate_signals(fused)
    assert out.loc[0, "rule__r"] == 0
    assert out.loc[1, "rule__r"] == 1
