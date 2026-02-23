# tests/test_feature_extraction_integration.py
import time
from data.tick_store import TickStore
from data.feature_store import FeatureStore
from scripts.extract_features import extract_for_symbol


def test_extract_and_save(tmp_path):
    ts = TickStore()
    fs = FeatureStore(base_dir=str(tmp_path))
    now = time.time()
    ticks = [
        {"timestamp": now, "price": 50.0, "size": 1},
        {"timestamp": now, "price": 51.0, "size": 2},
        {"timestamp": now, "price": 49.5, "size": 1},
    ]
    for t in ticks:
        ts.append_tick("EX1", t)
    ok = extract_for_symbol(ts, fs, "EX1", timeframe="1m")
    assert ok is True
    snap = fs.snapshot()
    assert "EX1__1m" in snap
    feats = fs.load_features("EX1", "1m")
    assert isinstance(feats, dict)
