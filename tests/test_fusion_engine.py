import pandas as pd
from modules.feature_engine.fusion_engine import FusionEngine


def test_join_fusion():
    f1 = pd.DataFrame({"timestamp": [1, 2], "a": [10, 20]})
    f2 = pd.DataFrame({"timestamp": [1, 2], "b": [100, 200]})

    fused = FusionEngine({"mode": "join"}).fuse({"t1": f1, "t2": f2})

    assert list(fused.columns) == ["timestamp", "a", "b"]
    assert fused.shape == (2, 3)


def test_weighted_fusion():
    f1 = pd.DataFrame({"timestamp": [1, 2], "signal": [1, 2]})
    f2 = pd.DataFrame({"timestamp": [1, 2], "signal": [2, 4]})

    cfg = {"mode": "weighted", "on": "timestamp", "weighted": {"signal": 1.0}}
    fused = FusionEngine(cfg).fuse({"x": f1, "y": f2})

    assert "weighted_fusion" in fused.columns
    assert fused.loc[0, "weighted_fusion"] == 1


def test_stacking_fusion():
    f1 = pd.DataFrame({"timestamp": [1], "a": [10]})
    f2 = pd.DataFrame({"timestamp": [1], "b": [20]})

    fused = FusionEngine({"mode": "stacking"}).fuse({"f1": f1, "f2": f2})

    assert "stack_vector" in fused.columns
    assert fused.loc[0, "stack_vector"] == [10, 20]
