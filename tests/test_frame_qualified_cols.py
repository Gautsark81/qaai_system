# tests/test_frame_qualified_cols.py
import pandas as pd
from modules.strategy.strategy_factory import StrategyFactory
from modules.feature_engine.fusion_engine import FusionEngine

def test_frame_qualified_column_resolution():
    # frames that when joined will produce signal_x and signal_y style names
    f1 = pd.DataFrame({"timestamp": [1, 2], "signal": [1, 2]})
    f2 = pd.DataFrame({"timestamp": [1, 2], "signal": [2, 4]})

    # perform join like FusionEngine would (this mirrors your earlier merge behavior)
    fused = FusionEngine({"mode": "join", "on": "timestamp"}).fuse({"x": f1, "y": f2})

    # Create a rule that targets x.signal explicitly (frame-qualified)
    cfg = {
        "rules": {
            "r_x_signal_high": {"op": ">", "col": "x.signal", "val": 1.5}
        },
        "signals": {
            "buy": {"rule": "r_x_signal_high", "value": 1}
        }
    }
    sf = StrategyFactory(cfg)
    out = sf.generate_signals(fused)

    # Expect: only rows where the x frame's signal > 1.5 flagged -> here, row index 1
    assert out.loc[0, "rule__r_x_signal_high"] == 0
    assert out.loc[1, "rule__r_x_signal_high"] == 1
    assert out.loc[1, "signal"] == 1
