from dataclasses import dataclass
from .enums import RiskLevel


@dataclass(frozen=True)
class RiskExposureFingerprint:
    max_position_pct: float
    avg_leverage: float
    stop_type: str
    stop_distance_pct: float
    tail_risk_exposure: RiskLevel
    capital_concentration: float
