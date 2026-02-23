from core.reproducibility.feature_fingerprint import compute_feature_hash
from core.reproducibility.parameter_fingerprint import compute_parameter_hash


def test_feature_hash_deterministic():
    config1 = {"a": 1, "b": 2}
    config2 = {"b": 2, "a": 1}

    assert compute_feature_hash(config1) == compute_feature_hash(config2)


def test_parameter_hash_deterministic():
    config1 = {"entry": "rsi", "exit": "ema"}
    config2 = {"exit": "ema", "entry": "rsi"}

    assert compute_parameter_hash(config1) == compute_parameter_hash(config2)