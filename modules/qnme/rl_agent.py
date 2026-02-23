# modules/qnme/rl_agent.py
"""
A conservative RL skeleton using PyTorch. The agent is intentionally simple:
- small MLP policy/value heads
- uses replay buffer from modules.qnme.learning (off-policy trainer)
- trainer is a skeleton: compute losses and optimize
This is a starting point — plug in algorithm of choice (DQN, DDPG, SAC) later.
"""

from typing import Dict, Any, List, Optional
import logging
import random

logger = logging.getLogger(__name__)

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    _TORCH_AVAILABLE = True
except Exception:
    _TORCH_AVAILABLE = False

from modules.qnme.learning import ReplayBuffer

if _TORCH_AVAILABLE:
    class MLP(nn.Module):
        def __init__(self, input_dim: int, hidden: int = 128, output_dim: int = 1):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, hidden),
                nn.ReLU(),
                nn.Linear(hidden, hidden),
                nn.ReLU(),
                nn.Linear(hidden, output_dim)
            )

        def forward(self, x):
            return self.net(x)

    class RLAgent:
        def __init__(self, state_dim: int, action_dim: int = 1, lr: float = 1e-3, gamma: float = 0.99):
            self.device = torch.device("cpu")
            self.policy = MLP(state_dim, hidden=128, output_dim=action_dim).to(self.device)
            self.value = MLP(state_dim, hidden=128, output_dim=1).to(self.device)
            self.opt = optim.Adam(list(self.policy.parameters()) + list(self.value.parameters()), lr=lr)
            self.gamma = gamma
            self.replay = ReplayBuffer(capacity=20000)

        def act(self, state, deterministic: bool = False):
            with torch.no_grad():
                x = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
                out = self.policy(x)
                return out.squeeze(0).cpu().numpy()

        def store_transition(self, entry: Dict[str, Any]):
            self.replay.push(entry)

        def train_step(self, batch_size: int = 64):
            if len(self.replay) < batch_size:
                return {}
            batch = self.replay.sample(batch_size)
            # build tensors
            states = torch.tensor([b["state"] for b in batch], dtype=torch.float32, device=self.device)
            actions = torch.tensor([b.get("action", 0.0) for b in batch], dtype=torch.float32, device=self.device).unsqueeze(-1)
            rewards = torch.tensor([b.get("reward", 0.0) for b in batch], dtype=torch.float32, device=self.device).unsqueeze(-1)
            next_states = torch.tensor([b["next_state"] for b in batch], dtype=torch.float32, device=self.device)

            # simple TD target with learned value
            values = self.value(states)
            next_values = self.value(next_states).detach()
            targets = rewards + self.gamma * next_values
            value_loss = nn.functional.mse_loss(values, targets)

            # policy loss: encourage actions that maximize predicted value (simple)
            # Here using policy as deterministic mapping -> maximize value(states, policy(states))
            pred_actions = self.policy(states)
            # combine pred_actions and compute pseudo-loss
            policy_loss = -self.value(states + pred_actions * 0.0).mean()  # placeholder, refine later

            loss = value_loss + 0.001 * policy_loss
            self.opt.zero_grad()
            loss.backward()
            self.opt.step()
            return {"value_loss": float(value_loss.detach().cpu().numpy()), "policy_loss": float(policy_loss.detach().cpu().numpy())}
else:
    # Minimal fallback: stubs with random actions
    class RLAgent:
        def __init__(self, state_dim: int, action_dim: int = 1, lr: float = 1e-3, gamma: float = 0.99):
            self.replay = ReplayBuffer(capacity=20000)

        def act(self, state, deterministic: bool = False):
            # random action placeholder
            return random.random()

        def store_transition(self, entry: Dict[str, Any]):
            self.replay.push(entry)

        def train_step(self, batch_size: int = 64):
            return {}
