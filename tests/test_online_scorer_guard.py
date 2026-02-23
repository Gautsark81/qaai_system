# tests/test_online_scorer_guard.py
from ml.online_scorer import OnlineScorer
class Dummy:
    def __init__(self):
        self.calls = 0
    def learn_one(self, x,y):
        self.calls += 1

def test_online_scorer_when_config_is_string_and_model_learn_one():
    m = Dummy()
    scorer = OnlineScorer(m, config="3")
    X = [{"f":1},{"f":2}]
    y = [0,1]
    assert scorer.learn(X,y) is True
    assert m.calls == 2
