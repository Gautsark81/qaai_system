from typing import List

from core.shadow.divergence.config import ShadowDivergenceConfig
from core.shadow.divergence.models import (
    SignalSnapshot,
    FillSnapshot,
    CapitalExpectation,
    CapitalReality,
)
from core.shadow.divergence.report import DivergenceReport


class ShadowDivergenceEngine:
    """
    Phase 13.3 — Shadow Divergence Engine.

    Observes signal vs execution vs capital reality.
    Produces explainable divergence evidence.
    """

    def __init__(self, *, config: ShadowDivergenceConfig | None = None):
        self._config = config or ShadowDivergenceConfig()

    @property
    def is_enabled(self) -> bool:
        return bool(self._config.enable_shadow_divergence)

    def evaluate(
        self,
        signal: SignalSnapshot,
        fill: FillSnapshot,
    ) -> DivergenceReport:
        if not self.is_enabled:
            return DivergenceReport(
                has_divergence=False,
                reasons=[],
            )

        reasons: List[str] = []

        # Symbol / side sanity (implicit contract)
        if signal.symbol != fill.symbol or signal.side != fill.side:
            reasons.append("symbol_or_side_mismatch")

        # Quantity divergence
        if signal.quantity != fill.quantity:
            reasons.append("quantity_mismatch")

        # Price slippage
        if signal.price > 0:
            slippage_pct = abs(fill.avg_price - signal.price) / signal.price * 100
            if slippage_pct > self._config.max_price_slippage_pct:
                reasons.append("price_slippage")

        return DivergenceReport(
            has_divergence=bool(reasons),
            reasons=reasons,
            has_execution_authority=False,
            has_capital_authority=False,
        )

    def evaluate_capital(
        self,
        *,
        expectation: CapitalExpectation,
        reality: CapitalReality,
    ) -> DivergenceReport:
        if not self.is_enabled:
            return DivergenceReport(
                has_divergence=False,
                reasons=[],
            )

        reasons: List[str] = []

        if expectation.expected_capital > 0:
            drift_pct = abs(
                reality.actual_capital - expectation.expected_capital
            ) / expectation.expected_capital * 100

            if drift_pct > self._config.max_capital_drift_pct:
                reasons.append("capital_drift")

        return DivergenceReport(
            has_divergence=bool(reasons),
            reasons=reasons,
            has_execution_authority=False,
            has_capital_authority=False,
        )
