# dashboard/adapters/strategy_view.py

from core.dashboard_read.snapshot import SystemSnapshot


def build_strategy_view(snapshot: SystemSnapshot):
    return [
        {
            "id": s.strategy_id,
            "status": s.status,
            "health": s.health_score,
            "drawdown": s.drawdown,
        }
        for s in snapshot.strategy_state.active
    ]
