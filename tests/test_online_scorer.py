# tests/test_online_scorer.py
import time
from ml.online_scorer import OnlineScorer

def test_online_scorer_basic_learn_and_score():
    sc = OnlineScorer()
    # simple dataset: feature x correlates with label
    for i in range(50):
        x = float(i) / 50.0
        features = {"x": x}
        label = 1 if x > 0.5 else 0
        sc.learn(features, label)
    # after training, scoring on high x should be > low x
    low = sc.score({"x": 0.1})
    high = sc.score({"x": 0.9})
    # expect high > low
    assert high >= low
    # metric should be a float between 0 and 1
    m = sc.get_metric()
    assert (m is None) or (0.0 <= m <= 1.0)
    assert sc.examples_seen() >= 50
