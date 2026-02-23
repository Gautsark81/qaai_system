from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass(frozen=True)
class OversightAnomaly:
    """
    Structured anomaly detected during oversight analysis.

    An anomaly is a *measurable deviation*.
    Observations may reference one or more anomalies.
    """

    anomaly_id: str
    anomaly_type: str              # DRIFT | SPIKE | DECAY | STALL | DIVERGENCE
    subject: str                   # strategy_id | capital | regime | governance

    baseline_value: float
    observed_value: float
    deviation_pct: float

    detected_at: datetime

    metadata: Dict[str, float]     # detector-specific metrics
    related_observation_id: Optional[str] = None
