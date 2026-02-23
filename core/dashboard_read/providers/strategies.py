from collections import defaultdict

from core.dashboard_read.snapshot import (
    StrategyState,
    StrategySnapshot,
)
from core.dashboard_read.providers._sources import strategies as strategies_source


def build_strategy_state() -> StrategyState:
    raw = strategies_source.read_strategy_snapshots()

    # If already StrategyState, return directly
    try:
        return StrategyState(
            active=raw.active,
            at_risk=raw.at_risk,
            retiring=raw.retiring,
            retired=raw.retired,
        )
    except AttributeError:
        pass

    buckets = defaultdict(list)

    for s in raw:
        buckets[s.status].append(
            StrategySnapshot(
                strategy_id=s.strategy_id,
                age_days=s.age_days,
                health_score=s.health_score,
                drawdown=s.drawdown,
                trailing_sl=s.trailing_sl,
                status=s.status,
            )
        )

    return StrategyState(
        active=buckets.get("active", []),
        at_risk=buckets.get("at_risk", []),
        retiring=buckets.get("retiring", []),
        retired=buckets.get("retired", []),
    )