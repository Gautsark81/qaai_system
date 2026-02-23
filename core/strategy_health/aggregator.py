from datetime import datetime
from typing import Iterable, List

from .contracts.dimension import HealthDimensionScore
from .contracts.snapshot import StrategyHealthSnapshot
from .contracts.enums import HealthStatus, DimensionVerdict
from .contracts.flags import HealthFlag


class StrategyHealthAggregator:
    """
    Aggregates dimension-level health into a single StrategyHealthSnapshot.

    This class encodes the HARD LAW of strategy health.
    No ML. No heuristics. No overrides.
    """

    def aggregate(
        self,
        *,
        strategy_id: str,
        as_of: datetime,
        dimensions: Iterable[HealthDimensionScore],
        trailing_metrics: dict[str, float],
        regime_context: str,
        confidence: float,
        version: str,
    ) -> StrategyHealthSnapshot:

        dimensions = list(dimensions)
        if not dimensions:
            raise ValueError("At least one HealthDimensionScore is required")

        # ---- Deterministic ordering ----
        dimensions_sorted = sorted(dimensions, key=lambda d: d.name)

        # ---- Weighted score calculation ----
        total_weight = sum(d.weight for d in dimensions_sorted)
        if total_weight <= 0:
            raise ValueError("Total dimension weight must be positive")

        weighted_score = sum(d.score * d.weight for d in dimensions_sorted)
        overall_score = weighted_score / total_weight

        # ---- Verdict resolution ----
        verdicts = [d.verdict for d in dimensions_sorted]

        if DimensionVerdict.FAIL in verdicts:
            status = HealthStatus.CRITICAL
        elif verdicts.count(DimensionVerdict.WARN) >= 2:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        # ---- Flag propagation (deterministic) ----
        flags: List[HealthFlag] = []
        for d in dimensions_sorted:
            if d.verdict in (DimensionVerdict.WARN, DimensionVerdict.FAIL):
                flags.append(
                    HealthFlag(
                        code=f"{d.name.upper()}_{d.verdict.value}",
                        severity="HIGH" if d.verdict == DimensionVerdict.FAIL else "MEDIUM",
                        message=f"{d.name} health marked as {d.verdict.value}",
                        dimension=d.name,
                    )
                )

        return StrategyHealthSnapshot(
            strategy_id=strategy_id,
            as_of=as_of,
            overall_score=round(overall_score, 4),
            status=status,
            dimensions={d.name: d for d in dimensions_sorted},
            trailing_metrics=dict(trailing_metrics),
            regime_context=regime_context,
            confidence=confidence,
            flags=flags,
            version=version,
        )
