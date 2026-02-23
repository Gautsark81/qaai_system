# core/strategy_factory/capital/productivity/productivity_model.py

from dataclasses import dataclass


def _safe_divide(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return a / b


def _clip(value: float) -> float:
    return round(value, 6)


@dataclass(frozen=True)
class ProductivitySnapshot:
    strategy_dna: str
    net_return: float
    avg_allocated_capital: float
    max_drawdown: float
    regime_confidence: float

    capital_efficiency: float
    risk_adjusted_efficiency: float
    regime_adjusted_efficiency: float


def compute_productivity_snapshot(
    *,
    strategy_dna: str,
    net_return: float,
    avg_allocated_capital: float,
    max_drawdown: float,
    regime_confidence: float,
) -> ProductivitySnapshot:

    capital_efficiency = _safe_divide(net_return, avg_allocated_capital)

    drawdown_penalty = abs(max_drawdown)

    risk_adjusted_efficiency = _safe_divide(
        net_return - drawdown_penalty,
        avg_allocated_capital,
    )

    regime_adjusted_efficiency = (
        risk_adjusted_efficiency * regime_confidence
    )

    return ProductivitySnapshot(
        strategy_dna=strategy_dna,
        net_return=net_return,
        avg_allocated_capital=avg_allocated_capital,
        max_drawdown=max_drawdown,
        regime_confidence=regime_confidence,
        capital_efficiency=_clip(capital_efficiency),
        risk_adjusted_efficiency=_clip(risk_adjusted_efficiency),
        regime_adjusted_efficiency=_clip(regime_adjusted_efficiency),
    )