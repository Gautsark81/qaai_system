from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Dict


@dataclass(frozen=True)
class EquityPoint:
    """
    Single point on the portfolio equity curve.
    """
    equity: float


@dataclass(frozen=True)
class DrawdownPoint:
    """
    Drawdown computed relative to historical peak equity.
    """
    drawdown_abs: float
    drawdown_pct: float


class PortfolioMetricsEngine:
    """
    Phase 13.1.3 — Portfolio Metrics Engine

    Responsibilities:
    - Build equity curve
    - Compute drawdowns
    - Compute rolling statistics

    Explicitly does NOT:
    - Allocate capital
    - Override risk
    - Touch execution
    """

    # -------------------------------------------------
    # Equity curve
    # -------------------------------------------------
    @staticmethod
    def equity_curve(equities: Iterable[float]) -> List[EquityPoint]:
        return [EquityPoint(equity=e) for e in equities]

    # -------------------------------------------------
    # Drawdown computation
    # -------------------------------------------------
    @staticmethod
    def drawdowns(equities: Iterable[float]) -> List[DrawdownPoint]:
        peak = float("-inf")
        result: List[DrawdownPoint] = []

        for equity in equities:
            if equity > peak:
                peak = equity

            dd_abs = peak - equity
            dd_pct = (dd_abs / peak) if peak > 0 else 0.0

            result.append(
                DrawdownPoint(
                    drawdown_abs=dd_abs,
                    drawdown_pct=dd_pct,
                )
            )

        return result

    # -------------------------------------------------
    # Rolling returns
    # -------------------------------------------------
    @staticmethod
    def rolling_returns(
        equities: List[float],
        window: int,
    ) -> List[float]:
        if window <= 1:
            raise ValueError("window must be > 1")

        returns: List[float] = []

        for i in range(window, len(equities)):
            prev = equities[i - window]
            curr = equities[i]

            if prev == 0:
                returns.append(0.0)
            else:
                returns.append((curr - prev) / prev)

        return returns

    # -------------------------------------------------
    # Rolling volatility (std of returns)
    # -------------------------------------------------
    @staticmethod
    def rolling_volatility(
        returns: List[float],
        window: int,
    ) -> List[float]:
        if window <= 1:
            raise ValueError("window must be > 1")

        vols: List[float] = []

        for i in range(window, len(returns) + 1):
            slice_ = returns[i - window : i]
            mean = sum(slice_) / window
            var = sum((r - mean) ** 2 for r in slice_) / window
            vols.append(var ** 0.5)

        return vols
