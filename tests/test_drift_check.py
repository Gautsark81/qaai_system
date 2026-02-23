# tests/test_drift_check.py
from data.feature_store import FeatureStore
from scripts.drift_check import run_check
import os


def test_drift_check_alert(tmp_path, monkeypatch):
    # create a FeatureStore with a high-drift artificial feature
    fs = FeatureStore(base_dir=str(tmp_path))
    # two features where lists are very different
    fs.save_features(
        "DR1",
        "1m",
        {
            "f1": [1, 1, 1, 1, 1, 1, 1, 1],
            "f2": [100, 100, 100, 100, 100, 100, 100, 100],
        },
    )
    # Monkeypatch FeatureStore used in drift_check to our tmp snapshot by setting env var
    os.environ["FEATURE_STORE_DIR"] = str(tmp_path)
    rc = run_check()
    # rc == 1 means alerts found
    assert rc == 1
