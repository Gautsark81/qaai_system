from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from core.capital.allocator import CapitalAllocator as HardCapitalGuard
from core.capital.allocation_curves.engine import CapitalAllocationCurveEngine

from core.lifecycle.contracts.state import LifecycleState
from core.ssr.contracts.enums import SSRStatus
from core.regime.taxonomy import MarketRegime
from core.regime.health import StrategyHealth


# ======================================================
# Capital Decision Vocabulary (STRING CONSTANTS)
# ======================================================

class _Decision:
    BLOCK = "BLOCK"
    REDUCE = "REDUCE"
    ALLOW = "ALLOW"


# ======================================================
# Capital Decision VALUE OBJECT (BACKWARD COMPATIBLE)
# ======================================================

@dataclass(frozen=True)
class CapitalDecision:
    """
    Immutable capital decision value object.

    NOTE:
    - Still available for legacy users
    - NOT returned directly by CapitalDecisionEngine
    """
    decision: str
    multiplier: float = 1.0
    reasons: Optional[List[str]] = None

    ALLOW = _Decision.ALLOW
    BLOCK = _Decision.BLOCK
    REDUCE = _Decision.REDUCE

    @classmethod
    def allow(cls, multiplier: float = 1.0, reasons: Optional[List[str]] = None):
        return cls(cls.ALLOW, multiplier, reasons or [])

    @classmethod
    def reduce(cls, multiplier: float, reasons: Optional[List[str]] = None):
        return cls(cls.REDUCE, multiplier, reasons or [])

    @classmethod
    def block(cls, reasons: Optional[List[str]] = None):
        return cls(cls.BLOCK, 0.0, reasons or [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "multiplier": self.multiplier,
            "reasons": self.reasons or [],
        }


# ======================================================
# FINAL CAPITAL DECISION CONTRACT (ENGINE OUTPUT)
# ======================================================

@dataclass(frozen=True)
class CapitalDecisionResult:
    """
    FINAL engine output.

    IMPORTANT (test-locked):
    - decision is a STRING ENUM (BLOCK / REDUCE / ALLOW)
    """
    strategy_id: str
    decision: str
    multiplier: float
    reasons: List[str]
    diagnostics: Dict[str, Any]


# ======================================================
# SAFE DEFAULTS
# ======================================================

class _NoOpRegimeConfidencePolicy:
    def multiplier_for(self, regime: MarketRegime) -> float:
        return 1.0


class _NoOpHardCapitalGuard:
    def allows(self, *_args, **_kwargs) -> bool:
        return True


# ======================================================
# Phase B5/B6 Capital Decision Engine
# ======================================================

class CapitalDecisionEngine:
    """
    Governance-first capital allocator.

    Guarantees:
    - Scalar decisions
    - Explainable reasoning
    - Regime + SSR governance
    - Risk dominance
    """

    def __init__(
        self,
        *,
        regime_confidence_policy: Optional[Any] = None,
        hard_capital_guard: Optional[Any] = None,
    ):
        self._regime_conf_policy = (
            regime_confidence_policy or _NoOpRegimeConfidencePolicy()
        )
        self._hard_guard = hard_capital_guard or _NoOpHardCapitalGuard()
        self._curve_engine = CapitalAllocationCurveEngine()

    # --------------------------------------------------
    # PUBLIC ENTRY POINT
    # --------------------------------------------------

    def decide(
        self,
        *,
        record: Any,
        health: Optional[StrategyHealth],
        confidence: Optional[float],
        regime: MarketRegime,
        risk_cap: Optional[float] = None,
        canary_freeze: bool = False,
    ) -> CapitalDecisionResult:

        reasons: List[str] = []
        diagnostics: Dict[str, Any] = {}

        strategy_id = getattr(record, "dna", "UNKNOWN")
        lifecycle_state = getattr(record, "state", None)

        # ==================================================
        # HARD GATES
        # ==================================================

        if lifecycle_state not in {None, "PAPER", "LIVE", "DEGRADED"}:
            return self._block(strategy_id, "Strategy not promoted", diagnostics)

        if canary_freeze:
            return self._block(strategy_id, "Canary freeze active", diagnostics)

        if health is None:
            return self._block(strategy_id, "No SSR data available", diagnostics)

        ssr = health.overall_ssr()
        diagnostics["ssr"] = ssr

        if ssr < 0.40:
            return self._block(strategy_id, "SSR below minimum", diagnostics)

        # ==================================================
        # REGIME COMPATIBILITY
        # ==================================================

        allowed_regimes = getattr(
            getattr(record, "spec", None),
            "allowed_regimes",
            None,
        )

        if allowed_regimes and regime not in allowed_regimes:
            if ssr < 0.70:
                return self._block(
                    strategy_id,
                    "Regime incompatible with weak SSR",
                    diagnostics,
                )
            reasons.append("Regime incompatible but SSR strong")

        # ==================================================
        # CONFIDENCE
        # ==================================================

        confidence = 0.5 if confidence is None else float(confidence)
        confidence = max(0.0, min(confidence, 1.0))
        diagnostics["confidence"] = confidence

        if confidence < 1.0:
            reasons.append("Confidence scaling applied")

        # ==================================================
        # REGIME MULTIPLIER
        # ==================================================

        regime_mult = self._regime_conf_policy.multiplier_for(regime)
        diagnostics["regime_multiplier"] = regime_mult
        diagnostics["regime"] = regime.name

        if regime_mult <= 0.0:
            return self._block(strategy_id, "Regime chaotic", diagnostics)

        # ==================================================
        # FINAL MULTIPLIER
        # ==================================================

        multiplier = ssr * confidence * regime_mult

        if risk_cap is not None:
            multiplier = min(multiplier, risk_cap)
            reasons.append("Risk cap applied")

        if multiplier <= 0.0:
            return self._block(
                strategy_id,
                "Risk block: zero capital",
                diagnostics,
            )

        # ==================================================
        # FINAL DECISION (TEST-LOCKED SEMANTICS)
        # ==================================================

        # Risk cap dominates permission
        if risk_cap is not None and risk_cap < 1.0:
            decision = CapitalDecision.REDUCE

        # Strong strategy promotion (no risk cap limiting)
        elif ssr >= 0.9 and confidence >= 1.0:
            decision = CapitalDecision.ALLOW
            multiplier = 1.0  # promote to full capital

        # Normal sizing-based decision
        else:
            decision = (
                CapitalDecision.ALLOW
                if multiplier >= 1.0
                else CapitalDecision.REDUCE
            )



        return CapitalDecisionResult(
            strategy_id=strategy_id,
            decision=decision,
            multiplier=round(multiplier, 4),
            reasons=reasons,
            diagnostics=diagnostics,
        )

    # --------------------------------------------------
    # INTERNAL
    # --------------------------------------------------

    def _block(
        self,
        strategy_id: str,
        reason: str,
        diagnostics: Dict[str, Any],
    ) -> CapitalDecisionResult:
        return CapitalDecisionResult(
            strategy_id=strategy_id,
            decision=CapitalDecision.BLOCK,
            multiplier=0.0,
            reasons=[reason],
            diagnostics=diagnostics,
        )
