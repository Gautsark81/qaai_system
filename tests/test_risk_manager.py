# tests/test_risk_manager.py
import pytest
import datetime as dt
from qaai_system.execution.risk_manager import RiskManager


@pytest.fixture
def rm():
    return RiskManager(
        {
            "starting_cash": 100000,
            "max_open_trades": 2,
            "max_position_size_pct": 0.1,
            "max_loss_per_trade": 5000,
            "max_symbol_weight": 0.2,
            "daily_loss_limit": 0.05,  # 5% of starting cash = 5000
            "min_equity_buffer": 20000,
            "max_drawdown_pct": 10,
        }
    )


def test_kill_switch(rm, tmp_path):
    # Boolean kill
    rm.set_kill_switch(True)
    assert rm.kill_switch_active()
    rm.clear_kill_switch()
    assert not rm.kill_switch_active()

    # File kill - set alias and actual attr to simulate test environments
    killfile = tmp_path / "ks.flag"
    # ensure file exists
    killfile.write_text("1")
    # set both attributes (some tests set _kill_switch_file)
    rm.kill_switch_file = str(killfile)
    rm._kill_switch_file = str(killfile)
    assert rm.kill_switch_active()
    # cleanup
    killfile.unlink()
    rm.kill_switch_file = None
    rm._kill_switch_file = None
    assert not rm.kill_switch_active()


def test_daily_loss_limit_blocks(rm):
    # Add trade history with -6000 PnL today
    rm.trade_history.append(
        {"symbol": "AAPL", "pnl": -6000, "timestamp": dt.datetime.now()}
    )
    assert not rm.is_trading_allowed(account_equity=50000)
    assert "Daily loss" in rm.circuit_reason()


def test_drawdown_trips_breaker(rm):
    rm._peak_equity = 100000
    rm.heartbeat(account_equity=85000)  # 15% drawdown
    assert rm.circuit_breaker_tripped()
    assert "Drawdown" in rm.circuit_reason()


def test_symbol_cap_blocks(rm):
    # 20% of 100k = 20k cap -> price 100 qty 300 -> 30k > cap
    with pytest.raises(ValueError):
        rm.check_symbol_cap("AAPL", qty=300, price=100, account_equity=100000)


def test_evaluate_risk_conditions(rm):
    # Large trade > position size cap
    ok, reason = rm.evaluate_risk(
        {"symbol": "AAPL", "price": 100, "quantity": 2000}, 100000
    )
    assert not ok and "Position too large" in reason

    # ATR loss too high
    ok, reason = rm.evaluate_risk(
        {"symbol": "AAPL", "price": 100, "quantity": 100, "atr": 100}, 100000
    )
    assert not ok and "ATR loss" in reason

    # Volatile regime limit
    ok, reason = rm.evaluate_risk(
        {"symbol": "AAPL", "price": 100, "quantity": 60}, 100000, regime_tag="volatile"
    )
    assert not ok and "volatile" in reason.lower()

    # Symbol cap breach
    rm.max_symbol_weight = 0.01
    ok, reason = rm.evaluate_risk(
        {"symbol": "AAPL", "price": 1000, "quantity": 20}, 100000
    )
    assert not ok and "RISK_BLOCK" in reason

    # Valid trade
    rm.max_symbol_weight = 0.5
    ok, reason = rm.evaluate_risk(
        {"symbol": "AAPL", "price": 100, "quantity": 50}, 100000
    )
    assert ok and "passed" in reason.lower()


def test_update_trade_log_and_exposure(rm):
    order = {
        "order_id": "O1",
        "symbol": "AAPL",
        "quantity": 10,
        "price": 100,
        "status": "open",
    }
    rm.update_trade_log(order)
    assert "O1" in rm.active_trades
    assert rm.get_open_risk_exposure() == 1000

    # Closing trade with PnL
    close = {"order_id": "O1", "symbol": "AAPL", "status": "closed", "pnl": 500}
    rm.update_trade_log(close)
    assert "O1" not in rm.active_trades
    assert any(t["pnl"] == 500 for t in rm.trade_history)


def test_diagnostics_snapshot(rm):
    rm.update_trade_log(
        {
            "order_id": "T1",
            "symbol": "AAPL",
            "quantity": 5,
            "price": 200,
            "status": "open",
        }
    )
    diag = rm.diagnostics()
    assert diag["open_trades"] == 1
    assert "AAPL" in diag["active_symbols"]
    assert "total_exposure" in diag
