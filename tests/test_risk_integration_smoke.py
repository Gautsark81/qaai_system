# path: tests/test_risk_integration_smoke.py

import pytest

from qaai_system.execution.execution_engine import ExecutionEngine
from qaai_system.portfolio.position_tracker import PositionTracker
from qaai_system.risk.risk_engine import RiskEngine
from qaai_system.risk.risk_limits import RiskLimits
from qaai_system.risk.risk_exceptions import CircuitBreakerTripped
from qaai_system.portfolio.portfolio_state import PortfolioState


class DummyLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def exception(self, *args, **kwargs):
        pass


def test_risk_engine_integration_via_execution_engine_on_fill():
    """
    Integration smoke test:

    - Build ExecutionEngine with attached PositionTracker + RiskEngine.
    - Simulate a losing trade via ee.on_fill(...)
    - Confirm RiskEngine now blocks trading (is_trading_allowed=False)
      and ensure_trading_allowed(...) raises CircuitBreakerTripped.
    """
    logger = DummyLogger()

    # Very tight daily loss limit so a single losing trade triggers kill-switch
    limits = RiskLimits(max_daily_loss=10.0)
    risk_engine = RiskEngine(limits=limits, logger=logger)

    # Minimal engine; we won't call process_signals in this test
    ee = ExecutionEngine(
        signal_engine=None,
        order_manager=None,
        broker_adapter=None,
        config={"exec_mode": "paper"},
    )

    position_tracker = PositionTracker(logger=logger)
    ee.position_tracker = position_tracker
    ee.risk_engine = risk_engine

    # Simulate a losing trade of -20 (greater than max_daily_loss=10)
    fill_event = {
        "trade_id": "T1",
        "symbol": "INFY",
        "side": "BUY",
        "filled_qty": 1,
        "avg_fill_price": 100.0,
        "pnl": -20.0,
        "close_reason": "SL",
        "status": "CLOSED",
    }

    ee.on_fill(fill_event)

    # Build a portfolio view from the tracker
    portfolio_state = PortfolioState.from_tracker(position_tracker)

    # RiskEngine should now consider trading disallowed
    assert risk_engine.is_trading_allowed(portfolio_state) is False

    # ensure_trading_allowed must raise CircuitBreakerTripped
    with pytest.raises(CircuitBreakerTripped):
        risk_engine.ensure_trading_allowed(portfolio_state)
