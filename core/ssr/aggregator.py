from datetime import datetime
from typing import Iterable, List

from .contracts.components import SSRComponentScore
from .contracts.snapshot import SSRSnapshot
from .contracts.enums import SSRStatus
from .contracts.flags import SSRFlag


class SSRAggregator:
    """
    Aggregates SSR component scores into a single SSRSnapshot.

    This class encodes the HARD LAW of Strategy Success Ratio.
    """

    def aggregate(
        self,
        *,
        strategy_id: str,
        as_of: datetime,
        components: Iterable[SSRComponentScore],
        trailing_metrics: dict[str, float],
        confidence: float,
        version: str,
    ) -> SSRSnapshot:

        components = list(components)
        if not components:
            raise ValueError("At least one SSRComponentScore is required")

        # ---- Deterministic ordering ----
        components_sorted = sorted(components, key=lambda c: c.name)

        # ---- Weighted SSR calculation ----
        total_weight = sum(c.weight for c in components_sorted)
        if total_weight <= 0:
            raise ValueError("Total component weight must be positive")

        weighted_sum = sum(c.score * c.weight for c in components_sorted)
        ssr_value = round(weighted_sum / total_weight, 4)

        # ---- Status resolution ----
        weak_components = [c for c in components_sorted if c.score < 0.50]
        failing_components = [c for c in components_sorted if c.score < 0.30]

        if failing_components:
            status = SSRStatus.FAILING
        elif len(weak_components) >= 2:
            status = SSRStatus.WEAK
        elif ssr_value >= 0.80:
            status = SSRStatus.STRONG
        else:
            status = SSRStatus.STABLE

        # ---- Flags (deterministic) ----
        flags: List[SSRFlag] = []

        for c in failing_components:
            flags.append(
                SSRFlag(
                    code=f"{c.name.upper()}_FAILING",
                    severity="HIGH",
                    message=f"{c.name} component below 0.30 threshold",
                    component=c.name,
                )
            )

        if status == SSRStatus.WEAK:
            for c in weak_components:
                flags.append(
                    SSRFlag(
                        code=f"{c.name.upper()}_WEAK",
                        severity="MEDIUM",
                        message=f"{c.name} component below 0.50 threshold",
                        component=c.name,
                    )
                )

        return SSRSnapshot(
            strategy_id=strategy_id,
            as_of=as_of,
            ssr=ssr_value,
            status=status,
            components={c.name: c for c in components_sorted},
            trailing_metrics=dict(trailing_metrics),
            confidence=confidence,
            flags=flags,
            version=version,
        )
