import pandas as pd
import pytest
from modules.strategy.strategy_factory import StrategyFactory
from modules.feature_engine.fusion_engine import FusionEngine

def test_strict_frame_matching_raises_on_unresolvable():
    f1 = pd.DataFrame({"timestamp": [1], "signal": [1]})
    fused = FusionEngine({"mode": "join", "on": "timestamp"}).fuse({"x": f1})

    cfg = {
        "frame_resolution": "strict",
        "rules": {
            # 'z' frame doesn't exist in fused columns -> should raise in strict mode
            "r": {"op": ">", "col": "z.signal", "val": 0}
        },
        "signals": {
            "buy": {"rule": "r", "value": 1}
        }
    }
    sf = StrategyFactory(cfg)
    with pytest.raises(ValueError):
        sf.generate_signals(fused)
