from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class StrategyTemplate:
    """
    Abstract alpha idea.
    """
    name: str
    alpha_stream: str
    timeframe: str
    base_params: Dict
