from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any
import uuid
import time


@dataclass(frozen=True)
class StrategySpec:
    """
    Canonical, immutable trading strategy definition.

    This object is:
    - Deterministic
    - JSON serializable
    - Mutation friendly
    """

    strategy_id: str = field(default_factory=lambda: f"strat_{uuid.uuid4().hex[:10]}")
    family: str = "generic"
    timeframe: str = "5m"

    universe: Dict[str, Any] = field(default_factory=dict)
    indicators: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    entry: Dict[str, Any] = field(default_factory=dict)
    exit: Dict[str, Any] = field(default_factory=dict)

    risk: Dict[str, Any] = field(default_factory=dict)

    targets: Dict[str, float] = field(default_factory=lambda: {
        "min_win_rate": 0.80,
        "min_pf": 1.4,
        "max_dd": 0.15,
    })

    lineage: Dict[str, Any] = field(default_factory=dict)

    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "family": self.family,
            "timeframe": self.timeframe,
            "universe": self.universe,
            "indicators": self.indicators,
            "entry": self.entry,
            "exit": self.exit,
            "risk": self.risk,
            "targets": self.targets,
            "lineage": self.lineage,
            "created_at": self.created_at,
        }
