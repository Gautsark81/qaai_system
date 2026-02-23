from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List

from core.oversight.contracts import OversightObservation, OversightAnomaly


# ======================================================
# Detector Config (Frozen, Explicit)
# ======================================================

@dataclass(frozen=True)
class CapitalDriftConfig:
    min_baseline_points: int = 5
    warning_threshold_pct: float = 25.0
    critical_threshold_pct: float = 50.0


# ======================================================
# Capital Drift Detector
# ======================================================

class CapitalDriftDetector:
    """
    Detects structural drift in capital allocation concentration.

    - Deterministic
    - Read-only
    - Snapshot-based
    """

    def __init__(self, config: CapitalDriftConfig = CapitalDriftConfig()):
        self._config = config

    def detect(
        self,
        *,
        snapshots: Iterable[Dict[str, float]],
        detected_at: datetime,
    ) -> List[OversightObservation]:

        snapshots = list(snapshots)

        if len(snapshots) < self._config.min_baseline_points:
            return []

        baseline = snapshots[:-1]
        current = snapshots[-1]

        observations: List[OversightObservation] = []

        for strategy_id, current_weight in current.items():
            history = [
                snap.get(strategy_id, 0.0)
                for snap in baseline
            ]

            baseline_avg = sum(history) / len(history)

            if baseline_avg == 0.0:
                continue

            deviation_pct = (
                (current_weight - baseline_avg) / baseline_avg
            ) * 100.0

            severity = None
            if abs(deviation_pct) >= self._config.critical_threshold_pct:
                severity = "CRITICAL"
            elif abs(deviation_pct) >= self._config.warning_threshold_pct:
                severity = "WARNING"

            if severity is None:
                continue

            anomaly = OversightAnomaly(
                anomaly_id=f"cap-drift-{strategy_id}",
                anomaly_type="DRIFT",
                subject=strategy_id,
                baseline_value=baseline_avg,
                observed_value=current_weight,
                deviation_pct=deviation_pct,
                detected_at=detected_at,
                metadata={
                    "window": len(history),
                },
            )

            observation = OversightObservation(
                observation_id=f"obs-cap-drift-{strategy_id}",
                category="CAPITAL",
                severity=severity,
                summary="Capital allocation drift detected",
                explanation=(
                    f"Strategy {strategy_id} capital allocation deviated "
                    f"by {deviation_pct:.1f}% from historical baseline"
                ),
                evidence_refs=[anomaly.anomaly_id],
                detected_at=detected_at,
                related_strategy_id=strategy_id,
            )

            observations.append(observation)

        return observations
