# core/alpha/screening/structural_evidence.py

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class StructuralRiskEvidence:
    symbol: str
    event_risk_flags: Tuple[str, ...]
    balance_sheet_flags: Tuple[str, ...]
    regulatory_flags: Tuple[str, ...]
