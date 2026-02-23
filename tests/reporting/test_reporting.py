from modules.reporting.health_api import strategy_health_snapshot
from modules.reporting.daily_report import daily_trading_report


class DummyTelemetry:
    def last_health(self):
        return type("H", (), {"health_score": 0.9, "flags": []})

    def last_state(self):
        return type("S", (), {"state": "ACTIVE"})

    def last_decay(self):
        return type("D", (), {"level": "NO_DECAY"})


def test_health_snapshot():
    snap = strategy_health_snapshot(DummyTelemetry())

    assert snap["health_score"] == 0.9
    assert snap["state"] == "ACTIVE"


class Trade:
    def __init__(self, pnl, dd):
        self.pnl = pnl
        self.equity_dd = dd


def test_daily_report():
    trades = [Trade(100, -10), Trade(-50, -30)]
    allocations = {"s1": 1.0, "s2": 0.0}

    report = daily_trading_report(trades=trades, allocations=allocations)

    assert report["total_trades"] == 2
    assert report["gross_pnl"] == 50
