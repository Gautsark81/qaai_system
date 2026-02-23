from datetime import datetime, timezone
import hashlib
from typing import Optional

from core.strategy_factory.promotion.scaling.capital_scaling_decision import (
    CapitalScalingDecision,
)
from core.strategy_factory.promotion.state_machine.promotion_state import (
    PromotionState,
)
from core.evidence.capital_scaling_audit_event import CapitalScalingAuditEvent


_SENTINEL = object()


class LiveCapitalScaler:
    """
    Phase 12 — Live Capital Scaling
    Deterministic, reversible, operator-governed.

    Phase 12.6:
    Governance chain embedding with backward compatibility.
    """

    MAX_DRAWDOWN = 0.30
    MIN_SSR = 0.70
    SCALE_UP_FACTOR = 1.25
    SCALE_DOWN_FACTOR = 0.75

    def evaluate(
        self,
        *,
        strategy,
        ssr_metrics,
        risk_envelope,
        current_capital: float,
        governance_chain_id: Optional[str] = _SENTINEL,
    ) -> CapitalScalingDecision:

        now = datetime.now(timezone.utc)

        # --------------------------------------------------
        # Phase 12.6 selective enforcement
        # --------------------------------------------------
        # If caller explicitly passed governance_chain_id=None → error
        if governance_chain_id is None:
            raise ValueError(
                "governance_chain_id is required for capital scaling decisions"
            )

        # If not provided (legacy call), treat as None
        if governance_chain_id is _SENTINEL:
            governance_chain_id = None

        # --------------------------------------------------
        # State validation
        # --------------------------------------------------
        if strategy.state != PromotionState.LIVE:
            return self._deny(
                strategy=strategy,
                previous_capital=current_capital,
                new_capital=current_capital,
                reason="INVALID_PROMOTION_STATE",
                explanation="Strategy not in LIVE state",
                now=now,
                governance_chain_id=governance_chain_id,
            )

        # --------------------------------------------------
        # Operator freeze
        # --------------------------------------------------
        if strategy.operator_veto:
            return self._deny(
                strategy=strategy,
                previous_capital=current_capital,
                new_capital=current_capital,
                reason="OPERATOR_FREEZE",
                explanation="Operator freeze active",
                now=now,
                governance_chain_id=governance_chain_id,
            )

        # --------------------------------------------------
        # Risk envelope
        # --------------------------------------------------
        if str(risk_envelope) != "SAFE":
            new_capital = current_capital * self.SCALE_DOWN_FACTOR
            return self._deny(
                strategy=strategy,
                previous_capital=current_capital,
                new_capital=new_capital,
                reason="RISK_ENVELOPE_UNSAFE",
                explanation="Risk envelope unsafe for scaling",
                now=now,
                governance_chain_id=governance_chain_id,
            )

        # --------------------------------------------------
        # Drawdown protection
        # --------------------------------------------------
        if ssr_metrics.drawdown >= self.MAX_DRAWDOWN:
            new_capital = current_capital * self.SCALE_DOWN_FACTOR
            return self._deny(
                strategy=strategy,
                previous_capital=current_capital,
                new_capital=new_capital,
                reason="DRAWDOWN_LIMIT_BREACHED",
                explanation="Drawdown exceeds scaling threshold",
                now=now,
                governance_chain_id=governance_chain_id,
            )

        # --------------------------------------------------
        # SSR decay protection
        # --------------------------------------------------
        if ssr_metrics.ssr < self.MIN_SSR:
            new_capital = current_capital * self.SCALE_DOWN_FACTOR
            return self._deny(
                strategy=strategy,
                previous_capital=current_capital,
                new_capital=new_capital,
                reason="SSR_DECAY",
                explanation="SSR below scaling threshold",
                now=now,
                governance_chain_id=governance_chain_id,
            )

        # --------------------------------------------------
        # SUCCESS — SCALE UP
        # --------------------------------------------------
        new_capital = current_capital * self.SCALE_UP_FACTOR

        checksum = self._checksum(
            strategy=strategy,
            ssr_metrics=ssr_metrics,
            risk_envelope=risk_envelope,
            previous_capital=current_capital,
            new_capital=new_capital,
            governance_chain_id=governance_chain_id,
        )

        audit = CapitalScalingAuditEvent(
            strategy_id=strategy.strategy_id,
            previous_capital=current_capital,
            new_capital=new_capital,
            scale_factor=self.SCALE_UP_FACTOR,
            decision_reason="CAPITAL_SCALE_UP",
            decision_checksum=checksum,
            timestamp=now,
            governance_chain_id=governance_chain_id,
        )

        return CapitalScalingDecision(
            allowed=True,
            scale_factor=self.SCALE_UP_FACTOR,
            reason="CAPITAL_SCALE_UP",
            explanation="Capital scaled up based on strong live performance",
            decision_checksum=checksum,
            timestamp=now,
            audit_event=audit,
            governance_chain_id=governance_chain_id,
        )

    # ------------------------------------------------------------------

    def _deny(
        self,
        *,
        strategy,
        previous_capital,
        new_capital,
        reason,
        explanation,
        now,
        governance_chain_id,
    ) -> CapitalScalingDecision:

        scale_factor = (
            new_capital / previous_capital if previous_capital > 0 else 1.0
        )

        payload = (
            f"{strategy.strategy_id}|"
            f"{reason}|"
            f"{scale_factor}|"
            f"{governance_chain_id}"
        )

        checksum = hashlib.sha256(payload.encode()).hexdigest()

        audit = CapitalScalingAuditEvent(
            strategy_id=strategy.strategy_id,
            previous_capital=previous_capital,
            new_capital=new_capital,
            scale_factor=scale_factor,
            decision_reason=reason,
            decision_checksum=checksum,
            timestamp=now,
            governance_chain_id=governance_chain_id,
        )

        return CapitalScalingDecision(
            allowed=False,
            scale_factor=scale_factor,
            reason=reason,
            explanation=explanation,
            decision_checksum=checksum,
            timestamp=now,
            audit_event=audit,
            governance_chain_id=governance_chain_id,
        )

    # ------------------------------------------------------------------

    def _checksum(
        self,
        *,
        strategy,
        ssr_metrics,
        risk_envelope,
        previous_capital,
        new_capital,
        governance_chain_id,
    ) -> str:
        payload = (
            f"{strategy.strategy_id}|"
            f"{strategy.state}|"
            f"{ssr_metrics.ssr}|"
            f"{ssr_metrics.drawdown}|"
            f"{risk_envelope}|"
            f"{previous_capital}|"
            f"{new_capital}|"
            f"{governance_chain_id}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()