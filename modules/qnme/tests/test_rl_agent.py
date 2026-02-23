# modules/qnme/tests/test_rl_agent.py
from modules.qnme.rl_agent import RLAgent
import numpy as np

def test_rl_agent_basic():
    agent = RLAgent(state_dim=4, action_dim=1)
    s = np.zeros(4).tolist()
    a = agent.act(s)
    assert a is not None
    # store dummy transitions and run train_step (should not crash)
    for i in range(20):
        agent.store_transition({"state":[0,0,0,0],"action":0.0,"reward":0.1,"next_state":[0,0,0,0]})
    stats = agent.train_step(batch_size=8)
    assert isinstance(stats, dict)
