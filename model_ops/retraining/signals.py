from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class RetrainingSignals:
    decay_detected: bool
    decay_reasons: List[str]
    shadow_divergence: float
    feature_drift_psi: float
