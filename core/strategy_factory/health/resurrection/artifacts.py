from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ResurrectionDecisionArtifact:
    """
    Immutable audit artifact representing a resurrection decision.

    This object is:
    - Append-only
    - Registry-safe
    - Dashboard-safe
    - Execution-agnostic

    IMPORTANT:
    - This artifact does NOT grant execution
    - It only records *why* a resurrection evaluation occurred
    """

    dna: str
    reason: str
    decay_score: float
    regime: str
    created_at: datetime

    # --------------------------------------------------
    # Factory
    # --------------------------------------------------

    @classmethod
    def from_inputs(
        cls,
        *,
        record: Any,
        decay_snapshot: Any,
        reason: str,
    ) -> "ResurrectionDecisionArtifact":
        """
        Construct a resurrection decision artifact from engine inputs.

        Parameters
        ----------
        record : StrategyRecord
            Strategy being evaluated
        decay_snapshot : DecaySnapshot
            Latest decay diagnostics
        reason : str
            Human-readable justification

        Returns
        -------
        ResurrectionDecisionArtifact
            Immutable audit artifact
        """

        if not hasattr(record, "dna"):
            raise TypeError(
                "Invalid record passed to ResurrectionDecisionArtifact"
            )

        if not hasattr(decay_snapshot, "decay_score"):
            raise TypeError(
                "Invalid decay_snapshot passed to ResurrectionDecisionArtifact"
            )

        if not isinstance(reason, str):
            raise TypeError(
                "ResurrectionDecisionArtifact reason must be a string"
            )

        return cls(
            dna=record.dna,
            reason=reason,
            decay_score=float(decay_snapshot.decay_score),
            regime=str(decay_snapshot.regime),
            created_at=datetime.utcnow(),
        )
