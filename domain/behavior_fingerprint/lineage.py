from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class LineageNode:
    strategy_id: str
    fingerprint_version: int
    mutation_type: str
    created_ts: datetime


@dataclass(frozen=True)
class StrategyLineage:
    strategy_id: str
    root_strategy_id: str
    ancestors: List[LineageNode]
    descendants: List[LineageNode]
