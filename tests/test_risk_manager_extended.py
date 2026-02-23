import time
from qaai_system.execution.risk_manager import RiskManager


def test_kill_switch_blocks():
    rm = RiskManager()
    assert rm.is_trading_allowed()
    rm.trigger_kill_switch("test")
    assert not rm.is_trading_allowed()
    assert "KillSwitch" in rm.circuit_reason()


def test_circuit_breaker_on_drawdown():
    rm = RiskManager(max_drawdown_pct=5.0)
    rm.circuit_break_on_drawdown(-6.0)
    assert not rm.is_trading_allowed()
    assert "Drawdown" in rm.circuit_reason()


def test_heartbeat_detection():
    rm = RiskManager({"heartbeat_interval": 1})
    rm.heartbeat()
    assert not rm.is_heartbeat_stale()
    time.sleep(1.2)
    assert rm.is_heartbeat_stale()
