# tests/test_daily_loss_reset.py
import datetime
from qaai_system.execution.risk_manager import RiskManager


def test_daily_loss_resets(monkeypatch):
    rm = RiskManager()

    # Set a fake current time (e.g., Aug 30, 2025 at 10:00)
    fake_now = datetime.datetime(2025, 8, 30, 10, 0, 0)
    monkeypatch.setattr(rm, "_now", lambda: fake_now)

    # Add trade on fake "today"
    rm.update_trade_log({"symbol": "AAPL", "pnl": -1000, "status": "closed"})
    assert rm.realized_today() == -1000

    # Advance fake time to the next day (Aug 31)
    monkeypatch.setattr(rm, "_now", lambda: fake_now + datetime.timedelta(days=1))
    assert rm.realized_today() == 0.0  # should auto-reset
