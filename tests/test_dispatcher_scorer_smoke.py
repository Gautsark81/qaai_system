# tests/test_dispatcher_scorer_smoke.py
from ml.online_scorer import OnlineScorer
from ml.drift_detector import DriftWatcher

def test_dispatcher_style_flow_smoke():
    scorer = OnlineScorer()
    drift = DriftWatcher()

    # simulate decision & outcome loop for 200 synthetic examples
    for i in range(200):
        features = {"price": float(i % 10), "vol": float((i % 5) + 1)}
        # get prob
        p = scorer.score(features)
        # simulate label: positive when price > 5
        label = 1 if features["price"] > 5.0 else 0
        scorer.learn(features, label)
        # update drift watcher with error-like metric
        auc = scorer.get_metric()
        if auc is not None:
            changed = drift.update(1.0 - auc)
            # change may or may not be detected; ensure update runs without exception
            assert isinstance(changed, bool)
    assert scorer.examples_seen() >= 200
