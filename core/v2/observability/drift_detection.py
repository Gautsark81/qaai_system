from __future__ import annotations
from typing import Dict, List
from .contracts import DriftSignal


class DriftDetector:
    """
    Deterministic drift detection.
    Compares baseline vs current metrics using absolute deltas.
    """

    SEVERITY_THRESHOLDS = {
        "LOW": 0.03,
        "MEDIUM": 0.07,
        "HIGH": 0.12,
    }

    def detect(self, baseline: Dict[str, float], current: Dict[str, float]) -> List[DriftSignal]:
        signals: List[DriftSignal] = []

        for metric, base_val in baseline.items():
            if metric not in current:
                continue

            cur_val = float(current[metric])
            base_val = float(base_val)
            delta = cur_val - base_val
            abs_delta = abs(delta)

            severity = "LOW"
            if abs_delta >= self.SEVERITY_THRESHOLDS["HIGH"]:
                severity = "HIGH"
            elif abs_delta >= self.SEVERITY_THRESHOLDS["MEDIUM"]:
                severity = "MEDIUM"

            signals.append(
                DriftSignal(
                    metric=metric,
                    baseline=base_val,
                    current=cur_val,
                    delta=delta,
                    severity=severity,
                )
            )

        return signals
