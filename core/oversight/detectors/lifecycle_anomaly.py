from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List

from core.oversight.contracts import OversightObservation
from core.strategy_factory.registry import StrategyRecord


# ======================================================
# Configuration
# ======================================================

@dataclass(frozen=True)
class LifecycleAnomalyConfig:
    stall_warning_days: int = 14
    stall_critical_days: int = 30
    oscillation_threshold: int = 3
    min_strong_ssr: float = 0.75
    min_strong_confidence: float = 0.80


# ======================================================
# Detector
# ======================================================

class StrategyLifecycleAnomalyDetector:
    """
    Detects lifecycle anomalies from StrategyRecord state + history.

    Guarantees:
    - Read-only
    - Deterministic
    - Evidence-driven
    - No speculative inference
    """

    def __init__(self, config: LifecycleAnomalyConfig = LifecycleAnomalyConfig()):
        self._config = config

    # ==================================================
    # Public API
    # ==================================================

    def detect(
        self,
        *,
        records: Iterable[StrategyRecord],
        detected_at: datetime,
    ) -> List[OversightObservation]:

        observations: List[OversightObservation] = []

        for record in records:
            observations.extend(
                self._detect_oscillation(record, detected_at)
            )
            observations.extend(
                self._detect_blocked_strength(record, detected_at)
            )
            observations.extend(
                self._detect_lifecycle_stall(record, detected_at)
            )

        return observations

    # ==================================================
    # Oscillation Detection
    # ==================================================

    def _detect_oscillation(
        self,
        record: StrategyRecord,
        now: datetime,
    ) -> List[OversightObservation]:

        history = record.history or []

        # Normalize transitions (ignore no-ops)
        transitions = [
            (t.get("from"), t.get("to"))
            for t in history
            if t.get("from") and t.get("to") and t.get("from") != t.get("to")
        ]

        if len(transitions) < self._config.oscillation_threshold:
            return []

        evidence = [f"{f}→{t}" for f, t in transitions]

        return [
            OversightObservation(
                observation_id=f"lifecycle-oscillation-{record.dna}",
                category="LIFECYCLE",
                severity="WARNING",
                summary="Strategy lifecycle oscillation detected",
                explanation=(
                    f"Strategy {record.dna} has oscillated "
                    f"{len(transitions)} times across lifecycle states"
                ),
                evidence_refs=evidence,
                detected_at=now,
                related_strategy_id=record.dna,
            )
        ]

    # ==================================================
    # Blocked Despite Strength
    # ==================================================

    def _detect_blocked_strength(
        self,
        record: StrategyRecord,
        now: datetime,
    ) -> List[OversightObservation]:

        ssr = getattr(record, "ssr", None)
        confidence = getattr(record, "confidence", None)
        state = getattr(record, "state", None)

        if ssr is None or confidence is None or state is None:
            return []

        if (
            ssr >= self._config.min_strong_ssr
            and confidence >= self._config.min_strong_confidence
            and state not in {"LIVE", "RETIRED"}
        ):
            return [
                OversightObservation(
                    observation_id=f"lifecycle-blocked-{record.dna}",
                    category="LIFECYCLE",
                    severity="WARNING",
                    summary="Strong strategy not promoted",
                    explanation=(
                        f"Strategy {record.dna} shows strong metrics "
                        f"(SSR={ssr:.2f}, confidence={confidence:.2f}) "
                        f"but remains in lifecycle state '{state}'"
                    ),
                    evidence_refs=[],
                    detected_at=now,
                    related_strategy_id=record.dna,
                )
            ]

        return []

    # ==================================================
    # Lifecycle Stall Detection
    # ==================================================

    def _detect_lifecycle_stall(
        self,
        record: StrategyRecord,
        now: datetime,
    ) -> List[OversightObservation]:

        since = getattr(record, "since", None)
        state = getattr(record, "state", None)

        if since is None or state is None:
            return []

        age_days = (now - since).days

        if age_days < self._config.stall_warning_days:
            return []

        if age_days >= self._config.stall_critical_days:
            severity = "CRITICAL"
        else:
            severity = "WARNING"

        return [
            OversightObservation(
                observation_id=f"lifecycle-stall-{record.dna}",
                category="LIFECYCLE",
                severity=severity,
                summary="Strategy lifecycle stall detected",
                explanation=(
                    f"Strategy {record.dna} has remained in state '{state}' "
                    f"for {age_days} days"
                ),
                evidence_refs=[f"state={state}", f"days={age_days}"],
                detected_at=now,
                related_strategy_id=record.dna,
            )
        ]
