# modules/qnme/tests/test_learning_replay.py
from modules.qnme.learning import ReplayBuffer, MicroRewardEngine

def test_replay_and_reward():
    rb = ReplayBuffer(capacity=10)
    for i in range(5):
        rb.push({"state": i, "action": "a", "reward": 0.1 * i})
    assert len(rb) == 5
    sample = rb.sample(3)
    assert len(sample) == 3

    m = MicroRewardEngine()
    r = m.compute_reward(1.0, 0.1, 0.01)
    assert isinstance(r, float)
