from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


# ======================================================
# Alpha Decay State Machine
# ======================================================

class AlphaDecayState(str, Enum):
    """
    Canonical decay classification.

    This enum is intentionally SMALL and STABLE.
    It is referenced by:
    - AlphaDecayDetector
    - RetirementEngine
    - ResurrectionEngine
    - Dashboards / audits
    """

    HEALTHY = "HEALTHY"
    EARLY_DECAY = "EARLY_DECAY"
    DECAYED = "DECAYED"
    TERMINAL = "TERMINAL"


# ======================================================
# Decay Snapshot (IMMUTABLE FACT)
# ======================================================

@dataclass(frozen=True)
class DecaySnapshot:
    """
    Immutable snapshot of decay analysis at a point in time.

    IMPORTANT:
    - This is a FACT, not a decision
    - Engines may interpret it differently
    - NEVER mutated after creation
    """

    dna: str
    decay_score: float
    historical_edge: float
    regime: str
    regime_shift_detected: bool
    data_expansion: bool
    timestamp: datetime
    notes: Optional[str] = None


# ======================================================
# Decay Evaluation Report (PUBLIC ARTIFACT)
# ======================================================

@dataclass(frozen=True)
class AlphaDecayReport:
    """
    Public, immutable decay evaluation result.

    This is the canonical output of AlphaDecayDetector.evaluate().
    """

    strategy_id: str

    # Canonical numeric decay score (0.0 → 1.0)
    score: float

    # Classified decay state
    state: AlphaDecayState

    # Confidence in decay assessment (0.0 → 1.0)
    confidence: float

    # Full diagnostic snapshot
    snapshot: DecaySnapshot

    # Evaluation timestamp
    evaluated_at: datetime


# ======================================================
# Alpha Decay Detector (PURE LOGIC)
# ======================================================

class AlphaDecayDetector:
    """
    Deterministic classifier converting raw signals
    into an AlphaDecayState.

    DESIGN RULES:
    - Stateless
    - No side effects
    - No registry access
    - No lifecycle mutation
    """

    # -----------------------------
    # Thresholds (GOVERNABLE)
    # -----------------------------

    EARLY_DECAY_THRESHOLD = 0.35
    DECAYED_THRESHOLD = 0.55
    TERMINAL_THRESHOLD = 0.80

    # --------------------------------------------------
    # Core Classification
    # --------------------------------------------------

    @classmethod
    def classify(cls, snapshot: DecaySnapshot) -> AlphaDecayState:
        score = snapshot.decay_score

        if score >= cls.TERMINAL_THRESHOLD:
            return AlphaDecayState.TERMINAL

        if score >= cls.DECAYED_THRESHOLD:
            return AlphaDecayState.DECAYED

        if score >= cls.EARLY_DECAY_THRESHOLD:
            return AlphaDecayState.EARLY_DECAY

        return AlphaDecayState.HEALTHY

    # --------------------------------------------------
    # Confidence Estimation (DETERMINISTIC)
    # --------------------------------------------------

    @staticmethod
    def compute_confidence(snapshot: DecaySnapshot) -> float:
        """
        Compute confidence of decay assessment.

        Confidence increases when:
        - Decay score is strong
        - Regime shift confirms signal
        - Data expansion validates robustness
        """

        confidence = min(1.0, max(0.0, snapshot.decay_score))

        if snapshot.regime_shift_detected:
            confidence += 0.15

        if snapshot.data_expansion:
            confidence += 0.10

        return min(confidence, 1.0)

    # --------------------------------------------------
    # Public API (STABLE CONTRACT)
    # --------------------------------------------------

    def evaluate(
        self,
        strategy_id: str,
        telemetry: Dict[str, Any],
    ) -> AlphaDecayReport:
        """
        Evaluate alpha decay from raw telemetry.
        """

        snapshot = DecaySnapshot(
            dna=strategy_id,
            decay_score=float(telemetry.get("performance_decay", 0.0)),
            historical_edge=float(telemetry.get("historical_edge", 0.0)),
            regime=str(telemetry.get("regime", "UNKNOWN")),
            regime_shift_detected=bool(
                telemetry.get("regime_shift_detected", False)
            ),
            data_expansion=bool(
                telemetry.get("data_expansion", False)
            ),
            timestamp=datetime.utcnow(),
            notes=None,
        )

        state = self.classify(snapshot)
        confidence = self.compute_confidence(snapshot)

        return AlphaDecayReport(
            strategy_id=strategy_id,
            score=snapshot.decay_score,
            state=state,
            confidence=confidence,
            snapshot=snapshot,
            evaluated_at=datetime.utcnow(),
        )
