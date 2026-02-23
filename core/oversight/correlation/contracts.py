# core/oversight/correlation/contracts.py

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class CorrelationSignal:
    """
    Canonical cross-domain anomaly correlation signal.

    This is a READ-ONLY oversight artifact.

    Guarantees:
    - Deterministic
    - Immutable
    - Explainable
    - Replay-safe
    - Regulator-readable

    This contract MUST NOT:
    - Trigger execution
    - Mutate state
    - Contain control logic
    """

    # ======================================================
    # Identity & Time
    # ======================================================

    timestamp: datetime
    strategy_id: str

    # ======================================================
    # Correlation Structure
    # ======================================================

    involved_domains: List[str]
    """
    Domains contributing to this signal.
    Examples:
    - ["capital"]
    - ["governance", "lifecycle"]
    - ["capital", "governance", "lifecycle"]
    """

    contributing_anomalies: List[str]
    """
    Stable identifiers of contributing anomaly signals.
    These MUST be human-readable and replay-stable.
    """

    # ======================================================
    # Risk Assessment
    # ======================================================

    severity: str
    """
    INFO | WARNING | CRITICAL

    Severity MUST be derived deterministically
    by policy (not ML, not heuristics).
    """

    confidence: float
    """
    0.0 → 1.0

    Represents correlation certainty, NOT prediction.
    """

    # ======================================================
    # Human Explanation
    # ======================================================

    narrative: str
    """
    Single-paragraph explanation answering:

    - What is happening?
    - Why now?
    - Why this matters?
    """

    recommended_actor: str
    """
    SYSTEM | OPERATOR | GOVERNANCE

    Indicates who should REVIEW this signal.
    This is NOT an instruction.
    """
