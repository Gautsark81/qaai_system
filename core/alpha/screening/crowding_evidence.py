# core/alpha/screening/crowding_evidence.py

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class CrowdingRiskEvidence:
    symbol: str
    institutional_crowding_flags: Tuple[str, ...]
    strategy_consensus_flags: Tuple[str, ...]
    positioning_fragility_flags: Tuple[str, ...]
