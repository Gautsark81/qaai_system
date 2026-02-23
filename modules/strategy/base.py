# modules/strategy/base.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional, Protocol


@dataclass
class Signal:
    """
    A simple signal object produced by strategies.
    You can easily map this to your OrderManager's create/send API.
    """
    strategy_id: str
    symbol: str
    side: str  # "BUY" | "SELL"
    size: float
    score: Optional[float] = None
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Strategy(Protocol):
    """
    Strategy interface (duck-typed Protocol so it's easier to test).
    Implementations should be simple, pure functions around feature input.
    """

    strategy_id: str

    def __init__(self, strategy_id: str, config: Dict[str, Any]):
        ...

    def prepare(self, historical_features: Iterable[Dict[str, Any]]) -> None:
        """
        Called with a sequence of historical feature rows (old -> recent).
        Use this to compute any stateful objects (rolling stats, scalers, etc.).
        This should be fast; heavy work belongs in offline model generation.
        """
        ...

    def generate_signals(self, latest_features: Dict[str, Any]) -> List[Signal]:
        """
        Given the latest features (single row), return 0..N Signals.
        """
        ...
