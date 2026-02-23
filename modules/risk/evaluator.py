# modules/risk/evaluator.py

from modules.risk.types import PortfolioSnapshot, MarketSnapshot
from modules.risk.limits import RiskLimits
from modules.risk.result import RiskResult


def evaluate_risk(
    *,
    desired_quantity: int,
    price: float,
    portfolio: PortfolioSnapshot,
    market: MarketSnapshot,
    limits: RiskLimits,
    symbol: str,
) -> RiskResult:
    """
    PURE, broker-agnostic, dominance-ordered risk evaluation.
    """

    # 1️⃣ Gross position sanity
    new_exposure = portfolio.gross_exposure + desired_quantity * price
    if new_exposure > portfolio.equity * limits.max_gross_exposure_pct:
        return RiskResult(False, None, "Position too large")

    # 2️⃣ ATR loss cap
    potential_loss = market.atr * desired_quantity
    if potential_loss > portfolio.equity * limits.max_atr_loss_pct:
        return RiskResult(False, None, "ATR loss exceeds limit")

    # 3️⃣ Volatility regime
    if market.volatility > limits.max_volatility:
        return RiskResult(False, None, "Volatility regime too high")

    # 4️⃣ Symbol concentration
    existing = portfolio.positions_by_symbol.get(symbol, 0)
    symbol_exposure = (existing + desired_quantity) * price
    if symbol_exposure > portfolio.equity * limits.max_symbol_pct:
        return RiskResult(False, None, "RISK_BLOCK")

    return RiskResult(True, desired_quantity, "Risk checks passed")
