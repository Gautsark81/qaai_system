from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from modules.capital.allocator import CapitalAllocator
from modules.capital.decision import CapitalDecision
from modules.capital.correlation_signal import CorrelationSignal
from modules.execution.portfolio_guard import PortfolioExecutionGuard
from modules.portfolio.metrics import PortfolioMetricsEngine
from modules.regime.signal import RegimeSignal
from modules.regime.detector import RegimeFeatures


@dataclass
class Phase13SIMOrchestrator:
    """
    Phase 13.5 — SIM Orchestrator (Portfolio Intelligence)

    This orchestrator:
    - Runs ONLY in SIM/BACKTEST
    - Aggregates all Phase-13 intelligence
    - Produces ONE CapitalDecision
    """

    capital_allocator: CapitalAllocator
    correlation_signal: CorrelationSignal
    regime_signal: RegimeSignal
    execution_guard: PortfolioExecutionGuard = PortfolioExecutionGuard()

    def evaluate(
        self,
        *,
        equities: List[float],
        volatility: float,
        cash_ratio: float,
        series: Dict[str, List[float]],
        weights: Dict[str, float],
        regime_features: RegimeFeatures,
        requested_notional: float,
    ) -> CapitalDecision:
        """
        Runs full Phase-13 intelligence stack and returns final decision.
        """

        # -----------------------------
        # 1. Base capital allocation
        # -----------------------------
        base_decision = self.capital_allocator.allocate(
            equities=equities,
            volatility=volatility,
            cash_ratio=cash_ratio,
            requested_notional=requested_notional,
        )

        if not base_decision.approved:
            return base_decision

        # -----------------------------
        # 2. Correlation / concentration
        # -----------------------------
        corr_scale, corr_reason = self.correlation_signal.scale_from_series(
            series=series,
            weights=weights,
        )

        # -----------------------------
        # 3. Regime modifier
        # -----------------------------
        regime_scale, regime_reason = self.regime_signal.evaluate(
            features=regime_features
        )

        # -----------------------------
        # 4. Aggregate scales
        # -----------------------------
        final_scale = (
            base_decision.scale_factor
            * corr_scale
            * regime_scale
        )

        final_scale = min(final_scale, 1.0)
        max_notional = requested_notional * final_scale

        reason = (
            f"{base_decision.reason} × "
            f"CORR={corr_scale:.2f} × "
            f"{regime_reason}"
        )

        return CapitalDecision(
            approved=True,
            max_notional=max_notional,
            scale_factor=final_scale,
            reason=reason,
        )
