# tests/test_feature_store.py
from data.feature_store import FeatureStore


def test_feature_save_and_load(tmp_path):
    fs = FeatureStore(base_dir=str(tmp_path))
    fs.save_features("AAA", "1m", {"ema": 12.3, "rsi": 55})
    loaded = fs.load_features("AAA", "1m")
    assert loaded.get("ema") == 12.3 and loaded.get("rsi") == 55


def test_snapshot_contains_saved(tmp_path):
    fs = FeatureStore(base_dir=str(tmp_path))
    fs.save_features("BBB", "1m", {"a": 1})
    snap = fs.snapshot()
    assert "BBB__1m" in snap
