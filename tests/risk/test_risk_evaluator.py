# tests/risk/test_risk_evaluator.py

from modules.risk.evaluator import evaluate_risk
from modules.risk.types import PortfolioSnapshot, MarketSnapshot
from modules.risk.limits import RiskLimits


def base_inputs():
    portfolio = PortfolioSnapshot(
        equity=100000,
        gross_exposure=20000,
        positions_by_symbol={"NIFTY": 10},
    )
    market = MarketSnapshot(atr=50, volatility=0.2)
    limits = RiskLimits(
        max_gross_exposure_pct=0.5,
        max_atr_loss_pct=0.02,
        max_volatility=0.5,
        max_symbol_pct=0.3,
    )
    return portfolio, market, limits


def test_gross_position_dominates():
    portfolio, market, limits = base_inputs()

    r = evaluate_risk(
        desired_quantity=1000,
        price=200,
        portfolio=portfolio,
        market=market,
        limits=limits,
        symbol="NIFTY",
    )

    assert not r.allowed
    assert r.reason == "Position too large"


def test_atr_checked_before_volatility():
    portfolio, market, limits = base_inputs()

    r = evaluate_risk(
        desired_quantity=100,
        price=100,
        portfolio=portfolio,
        market=market,
        limits=limits,
        symbol="BANKNIFTY",
    )

    assert not r.allowed
    assert r.reason == "ATR loss exceeds limit"


def test_success_path_reason():
    portfolio, market, limits = base_inputs()

    r = evaluate_risk(
        desired_quantity=1,
        price=100,
        portfolio=portfolio,
        market=market,
        limits=limits,
        symbol="FINNIFTY",
    )

    assert r.allowed
    assert r.reason == "Risk checks passed"
