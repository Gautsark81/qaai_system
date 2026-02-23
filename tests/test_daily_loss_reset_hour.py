# tests/test_daily_loss_reset_hour.py
import datetime
from qaai_system.execution.risk_manager import RiskManager


def test_reset_hour_triggers(monkeypatch):
    # Set reset hour to 6 AM
    rm = RiskManager(config={"reset_hour": 6})

    # Set fake time: before reset
    before_reset = datetime.datetime(2025, 8, 30, 5, 0, 0)
    monkeypatch.setattr(rm, "_now", lambda: before_reset)

    rm.update_trade_log({"symbol": "AAPL", "pnl": -500, "status": "closed"})
    assert rm.realized_today() == -500

    # Advance to after reset boundary
    after_reset = datetime.datetime(2025, 8, 30, 7, 0, 0)
    monkeypatch.setattr(rm, "_now", lambda: after_reset)

    # Now it should reset
    assert rm.realized_today() == 0.0
