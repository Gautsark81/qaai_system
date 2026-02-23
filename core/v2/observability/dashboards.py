from __future__ import annotations
from typing import List, Dict
from .contracts import StrategyObservabilitySnapshot, DriftSignal, AlphaDecayReport


class ObservabilityDashboardBuilder:
    """
    Builds operator-safe observability snapshots.
    Read-only. No side effects.
    """

    def build(
        self,
        *,
        strategy_id: str,
        alpha_verdict: str,
        drift_signals: List[DriftSignal],
        decay: AlphaDecayReport,
    ) -> StrategyObservabilitySnapshot:

        flags = []
        for s in drift_signals:
            if s.severity in ("MEDIUM", "HIGH"):
                flags.append(f"{s.metric.upper()}_DRIFT")

        notes: Dict[str, str] = {}
        if decay.status != "STABLE":
            notes["decay"] = f"Alpha {decay.status.lower()}"

        return StrategyObservabilitySnapshot(
            strategy_id=strategy_id,
            alpha_verdict=alpha_verdict,
            drift_flags=flags,
            decay_status=decay.status,
            notes=notes,
        )
