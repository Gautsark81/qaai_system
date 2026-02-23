from datetime import datetime
from typing import Iterable, Tuple
import hashlib
import json

from .models import StrategyCapitalView, PortfolioCapitalPosture
from .snapshot import CapitalGovernanceSnapshot


def _freeze(
    views: Iterable[StrategyCapitalView],
) -> Tuple[StrategyCapitalView, ...]:
    return tuple(views)


def _snapshot_version(
    views: Tuple[StrategyCapitalView, ...],
) -> str:
    payload = tuple(
        map(
            lambda v: (
                v.strategy_id,
                v.allocated_capital,
                v.utilized_capital,
                v.drawdown,
            ),
            views,
        )
    )
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()


def build_portfolio_capital_posture(
    strategy_views: Iterable[StrategyCapitalView],
) -> CapitalGovernanceSnapshot:
    frozen = _freeze(strategy_views)

    per_strategy = dict(
        map(lambda v: (v.strategy_id, v), frozen)
    )

    allocated = tuple(map(lambda v: v.allocated_capital, frozen))
    utilized = tuple(map(lambda v: v.utilized_capital, frozen))
    drawdowns = tuple(map(lambda v: v.drawdown, frozen))

    posture = PortfolioCapitalPosture(
        total_allocated=sum(allocated),
        total_utilized=sum(utilized),
        max_drawdown=max(drawdowns) if drawdowns else 0.0,
        per_strategy=per_strategy,
    )

    return CapitalGovernanceSnapshot(
        posture=posture,
        correlation_and_concentration=None,
        stress_envelope=None,
        generated_at=datetime.utcnow(),
        snapshot_version=_snapshot_version(frozen),
    )
