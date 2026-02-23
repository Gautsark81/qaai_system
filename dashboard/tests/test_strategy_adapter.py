# dashboard/tests/test_strategy_adapter.py

from core.dashboard_read.snapshot import StrategySnapshot, StrategyState, SystemSnapshot
from dashboard.adapters.strategy_view import build_strategy_view


def test_strategy_adapter_is_passive(snapshot_factory):
    snapshot = snapshot_factory(
        strategy_state=StrategyState(
            active=[
                StrategySnapshot(
                    strategy_id="S1",
                    age_days=10,
                    health_score=0.8,
                    drawdown=0.1,
                    trailing_sl=95.0,
                    status="active",
                )
            ],
            at_risk=[],
            retiring=[],
            retired=[],
        )
    )

    view = build_strategy_view(snapshot)

    assert view[0]["health"] == 0.8
    assert view[0]["status"] == "active"
