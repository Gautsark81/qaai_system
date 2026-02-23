from dataclasses import dataclass
from typing import Dict


@dataclass
class PortfolioExposure:
    total_deployed: float
    per_symbol: Dict[str, float]
