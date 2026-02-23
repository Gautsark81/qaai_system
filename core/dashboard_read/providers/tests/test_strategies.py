from core.dashboard_read.providers.strategies import build_strategy_state
from core.dashboard_read.snapshot import StrategyState


def test_strategy_state(monkeypatch):
    class DummyStrategy:
        def __init__(self, sid, status):
            self.strategy_id = sid
            self.age_days = 10
            self.health_score = 0.8
            self.drawdown = 0.1
            self.trailing_sl = 95.0
            self.status = status

    dummy = [
        DummyStrategy("S1", "active"),
        DummyStrategy("S2", "at_risk"),
        DummyStrategy("S3", "retiring"),
        DummyStrategy("S4", "retired"),
    ]

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.strategies.read_strategy_snapshots",
        lambda: dummy,
    )

    state = build_strategy_state()

    assert isinstance(state, StrategyState)
    assert len(state.active) == 1
    assert len(state.at_risk) == 1
    assert len(state.retiring) == 1
    assert len(state.retired) == 1
