# core/strategy_reputation/strategy_identity.py
from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyIdentity:
    strategy_id: str
    name: str
    version: str
    author: str
