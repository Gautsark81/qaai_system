# path: tests/test_risk_engine.py
import math

from qaai_system.risk.risk_engine import RiskEngine
from qaai_system.risk.risk_limits import RiskLimits
from qaai_system.risk.risk_state import RiskState
from qaai_system.risk.risk_exceptions import CircuitBreakerTripped


class DummyPortfolio:
    def __init__(self, equity, realized_pnl=0.0, positions=None):
        self.equity = equity
        self.realized_pnl = realized_pnl
        self.positions = positions or {}


def test_daily_loss_trips_kill_switch_and_blocks_trading():
    limits = RiskLimits(max_daily_loss=1000.0)
    state = RiskState()
    engine = RiskEngine(limits=limits, state=state)

    pf = DummyPortfolio(equity=100000.0, realized_pnl=0.0)

    # Initially trading allowed
    assert engine.is_trading_allowed(pf) is True

    # Register a loss of -1200 => beyond daily loss
    engine.register_fill(realized_pnl=-1200.0, portfolio=pf)

    assert engine.is_trading_allowed(pf) is False
    assert engine.state.kill_switch is True
    assert engine.state.kill_reason in ("DAILY_LOSS_ABS", "DAILY_LOSS_PCT")

    # ensure_trading_allowed should now raise
    try:
        engine.ensure_trading_allowed(pf)
        assert False, "Expected CircuitBreakerTripped"
    except CircuitBreakerTripped:
        pass


def test_order_blocked_by_symbol_weight_and_order_notional():
    limits = RiskLimits(
        max_symbol_weight=0.25,          # 25% of equity per symbol
        max_order_notional_pct=0.20,     # 20% of equity per order
    )
    engine = RiskEngine(limits=limits)

    # Equity = 100k, existing position: 20k in INFY (20% weight)
    positions = {
        "INFY": {
            "quantity": 20,
            "avg_price": 1000.0,
            "side": "LONG",
        }
    }
    pf = DummyPortfolio(equity=100000.0, realized_pnl=0.0, positions=positions)

    # New order: BUY 100 @ 1000 -> notional 100k
    res = engine.evaluate_order(
        symbol="INFY",
        side="BUY",
        quantity=100,
        price=1000.0,
        portfolio=pf,
    )

    assert res.allowed is False
    # Should have at least one hard breach (order too big / symbol too heavy)
    assert any("SYMBOL_WEIGHT" in b for b in res.hard_breaches) or any(
        "ORDER_NOTIONAL_PCT" in b for b in res.hard_breaches
    )


def test_max_open_positions_blocks_new_symbol():
    limits = RiskLimits(max_open_positions=2)
    engine = RiskEngine(limits=limits)

    positions = {
        "INFY": {"quantity": 10, "avg_price": 1000.0, "side": "LONG"},
        "RELIANCE": {"quantity": 5, "avg_price": 2500.0, "side": "LONG"},
    }
    pf = DummyPortfolio(equity=200000.0, positions=positions)

    # Trying to open a third symbol should be blocked
    res = engine.evaluate_order(
        symbol="SBIN",
        side="BUY",
        quantity=10,
        price=500.0,
        portfolio=pf,
    )
    assert res.allowed is False
    assert any("OPEN_POSITIONS" in b for b in res.hard_breaches)


def test_gross_and_net_exposure_limits():
    limits = RiskLimits(
        max_gross_exposure_pct=1.0,  # 100% of equity
        max_net_exposure_pct=0.5,    # 50% of equity
    )
    engine = RiskEngine(limits=limits)

    # Equity = 100k, current gross=50k long, net=50k long
    positions = {
        "INFY": {"quantity": 50, "avg_price": 1000.0, "side": "LONG"},
    }
    pf = DummyPortfolio(equity=100000.0, positions=positions)

    # New BUY 60k -> new gross=110k ( > 100% ), new net=110k (> 50% )
    res = engine.evaluate_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=24,
        price=2500.0,  # 24 * 2500 = 60k
        portfolio=pf,
    )

    assert res.allowed is False
    assert any("GROSS_EXPOSURE" in b for b in res.hard_breaches)
    assert any("NET_EXPOSURE" in b for b in res.hard_breaches)


def test_strategy_specific_daily_loss_trips_kill_switch():
    limits = RiskLimits(
        max_strategy_daily_loss={"stratA": 100.0},
    )
    engine = RiskEngine(limits=limits)

    pf = DummyPortfolio(equity=50000.0)

    # Loss in a different strategy should not trip 'stratA' limit
    engine.register_fill(realized_pnl=-200.0, portfolio=pf, strategy_id="stratB")
    assert engine.state.kill_switch is False

    # Loss in stratA should trip the strategy-specific limit
    engine.register_fill(realized_pnl=-150.0, portfolio=pf, strategy_id="stratA")
    assert engine.state.kill_switch is True
    assert engine.state.kill_reason in ("STRATEGY_DAILY_LOSS", "STRATEGY_DAILY_LOSS_PCT")


def test_intraday_drawdown_limit_blocks_trading():
    limits = RiskLimits(
        max_intraday_drawdown_pct=0.20,   # -20% from start-of-day equity
    )
    engine = RiskEngine(limits=limits)

    # Start of day: equity = 100k
    pf_start = DummyPortfolio(equity=100000.0)
    assert engine.is_trading_allowed(pf_start) is True

    # Simulate equity drop to 75k -> -25% drawdown, beyond 20%
    pf_late = DummyPortfolio(equity=75000.0)
    engine.register_fill(realized_pnl=-25000.0, portfolio=pf_late, strategy_id="stratX")

    assert engine.is_trading_allowed(pf_late) is False
    assert engine.state.kill_switch is True
    assert engine.state.kill_reason == "DAILY_DRAWDOWN"


def test_manual_kill_helper_sets_kill_switch():
    engine = RiskEngine(limits=RiskLimits())

    pf = DummyPortfolio(equity=100000.0)
    assert engine.is_trading_allowed(pf) is True

    engine.set_kill_switch(reason="MANUAL_KILL_FROM_TEST")

    assert engine.is_trading_allowed(pf) is False
    assert engine.state.kill_switch is True
    assert engine.state.kill_reason == "MANUAL_KILL_FROM_TEST"

    # Clearing should re-enable trading (assuming no other limits hit)
    engine.clear_kill_switch()
    assert engine.is_trading_allowed(pf) is True
