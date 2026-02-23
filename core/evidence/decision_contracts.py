# core/evidence/decision_contracts.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, Union
import json
import hashlib


CanonicalFactors = Optional[Tuple[Tuple[str, Any], ...]]


@dataclass(frozen=True)
class DecisionEvidence:
    decision_id: str
    decision_type: str
    timestamp: Optional[datetime]

    # Strategy context
    strategy_id: Optional[str] = None
    alpha_stream: Optional[str] = None

    # Regime context
    market_regime: Optional[str] = None
    regime_confidence: Optional[float] = None
    drift_detected: Optional[bool] = None

    # Capital context
    requested_weight: Optional[float] = None
    approved_weight: Optional[float] = None
    capital_available: Optional[float] = None

    # Quality metrics
    ssr: Optional[float] = None
    confidence: Optional[float] = None
    risk_score: Optional[float] = None

    # Governance
    governance_required: Optional[bool] = None
    governance_status: Optional[str] = None
    reviewer: Optional[str] = None
    rationale: Optional[str] = None

    # Evidence graph
    factors: Union[Dict[str, Any], CanonicalFactors, None] = None
    parent_decision_id: Optional[str] = None

    # Integrity
    checksum: str = field(default="__AUTO__")

    # ======================================================
    # POST INIT
    # ======================================================

    def __post_init__(self):

        # Normalize timestamp if present (do NOT require it)
        if self.timestamp is not None:
            object.__setattr__(
                self,
                "timestamp",
                self.timestamp.replace(microsecond=0),
            )

        # Canonicalize factors safely
        canonical = self._canonicalize_factors(self.factors)
        object.__setattr__(self, "factors", canonical)

        # Compute checksum if auto
        if self.checksum in (None, "__AUTO__"):
            object.__setattr__(self, "checksum", self._compute_checksum())

    # ======================================================
    # CHECKSUM LOGIC (STRICTLY DETERMINISTIC)
    # ======================================================

    def _compute_checksum(self) -> str:
        """
        IMPORTANT:
        Timestamp is intentionally excluded.
        Checksum must reflect semantic decision content only.
        """

        payload = {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type,
            "strategy_id": self.strategy_id,
            "alpha_stream": self.alpha_stream,
            "market_regime": self.market_regime,
            "regime_confidence": self.regime_confidence,
            "drift_detected": self.drift_detected,
            "requested_weight": self.requested_weight,
            "approved_weight": self.approved_weight,
            "capital_available": self.capital_available,
            "ssr": self.ssr,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "governance_required": self.governance_required,
            "governance_status": self.governance_status,
            "reviewer": self.reviewer,
            "rationale": self.rationale,
            "parent_decision_id": self.parent_decision_id,
            "factors": self.factors,
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(encoded).hexdigest()

    # ======================================================
    # FACTOR CANONICALIZATION
    # ======================================================

    @staticmethod
    def _canonicalize_factors(
        factors: Union[Dict[str, Any], CanonicalFactors, None]
    ) -> CanonicalFactors:

        if not factors:
            return None

        # Already canonical tuple-of-tuples
        if isinstance(factors, tuple):
            return tuple(sorted(tuple(pair) for pair in factors))

        # Dict → canonical tuple
        if isinstance(factors, dict):
            return tuple(sorted(factors.items()))

        raise TypeError(
            "factors must be dict, tuple-of-tuples, or None"
        )