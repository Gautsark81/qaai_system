from datetime import datetime
from typing import Iterable, Tuple
import hashlib
import json

from core.capital.stress.stress_report import StressReport

from .models import (
    StrategyStressContribution,
    PortfolioStressEnvelope,
)
from .snapshot import CapitalGovernanceSnapshot


def _freeze(
    reports: Iterable[StressReport],
) -> Tuple[StressReport, ...]:
    return tuple(reports)


def _version_key(
    reports: Tuple[StressReport, ...],
) -> str:
    payload = tuple(
        map(
            lambda r: (
                r.strategy_id,
                r.worst_case_loss,
                r.scenario,
            ),
            reports,
        )
    )
    return hashlib.sha256(
        json.dumps(payload).encode()
    ).hexdigest()


def build_portfolio_stress_envelope(
    reports: Iterable[StressReport],
) -> CapitalGovernanceSnapshot:
    """
    Advisory-only portfolio stress envelope.

    Guarantees:
    - Read-only
    - Deterministic
    - No execution authority
    """

    frozen = _freeze(reports)

    contributions = tuple(
        map(
            lambda r: StrategyStressContribution(
                strategy_id=r.strategy_id,
                worst_case_loss=r.worst_case_loss,
                scenario=r.scenario,
            ),
            frozen,
        )
    )

    envelope = PortfolioStressEnvelope(
        per_strategy=contributions,
        total_worst_case_loss=sum(
            map(lambda c: c.worst_case_loss, contributions)
        ),
        scenario_count=len(contributions),
    )

    return CapitalGovernanceSnapshot(
        posture=None,
        correlation_and_concentration={},
        stress_envelope=envelope,
        generated_at=datetime.utcnow(),
        snapshot_version=_version_key(frozen),
    )
