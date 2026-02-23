from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Dict

from core.evidence.decision_contracts import DecisionEvidence
from core.oversight.contracts import OversightObservation


# ======================================================
# Configuration
# ======================================================

@dataclass(frozen=True)
class GovernanceFrictionConfig:
    latency_warning_hours: float = 24.0
    latency_critical_hours: float = 72.0
    reversal_window_hours: float = 12.0


# ======================================================
# Detector
# ======================================================

class GovernanceFrictionDetector:
    """
    Detects governance latency, stalls, and reversals.

    - Read-only
    - Deterministic
    - Evidence-driven
    """

    def __init__(self, config: GovernanceFrictionConfig = GovernanceFrictionConfig()):
        self._config = config

    def detect(
        self,
        *,
        decisions: Iterable[DecisionEvidence],
        detected_at: datetime,
    ) -> List[OversightObservation]:

        decisions = sorted(decisions, key=lambda d: d.timestamp)
        observations: List[OversightObservation] = []

        by_strategy: Dict[str, List[DecisionEvidence]] = {}
        for d in decisions:
            by_strategy.setdefault(d.strategy_id, []).append(d)

        for strategy_id, history in by_strategy.items():
            observations.extend(
                self._detect_latency(history, detected_at, strategy_id)
            )
            observations.extend(
                self._detect_reversals(history, strategy_id)
            )

        return observations

    # --------------------------------------------------

    def _detect_latency(
        self,
        history: List[DecisionEvidence],
        now: datetime,
        strategy_id: str,
    ) -> List[OversightObservation]:

        observations: List[OversightObservation] = []

        last = history[-1]
        age = now - last.timestamp

        severity = None
        if age >= timedelta(hours=self._config.latency_critical_hours):
            severity = "CRITICAL"
        elif age >= timedelta(hours=self._config.latency_warning_hours):
            severity = "WARNING"

        if severity:
            observations.append(
                OversightObservation(
                    observation_id=f"gov-latency-{strategy_id}",
                    category="GOVERNANCE",
                    severity=severity,
                    summary="Governance decision latency detected",
                    explanation=(
                        f"No governance decision for strategy {strategy_id} "
                        f"in {age.total_seconds() / 3600:.1f} hours"
                    ),
                    evidence_refs=[last.decision_id],
                    detected_at=now,
                    related_strategy_id=strategy_id,
                )
            )

        return observations

    # --------------------------------------------------

    def _detect_reversals(
        self,
        history: List[DecisionEvidence],
        strategy_id: str,
    ) -> List[OversightObservation]:

        observations: List[OversightObservation] = []

        for prev, curr in zip(history, history[1:]):
            if prev.decision_type == curr.decision_type:
                continue

            delta = curr.timestamp - prev.timestamp
            if delta <= timedelta(hours=self._config.reversal_window_hours):
                observations.append(
                    OversightObservation(
                        observation_id=f"gov-reversal-{strategy_id}",
                        category="GOVERNANCE",
                        severity="WARNING",
                        summary="Rapid governance reversal detected",
                        explanation=(
                            f"Decision for strategy {strategy_id} reversed "
                            f"within {delta.total_seconds() / 3600:.1f} hours"
                        ),
                        evidence_refs=[
                            prev.decision_id,
                            curr.decision_id,
                        ],
                        detected_at=curr.timestamp,
                        related_strategy_id=strategy_id,
                    )
                )

        return observations
