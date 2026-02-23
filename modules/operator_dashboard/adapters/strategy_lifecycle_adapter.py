from typing import Dict
from datetime import datetime, timezone

from core.strategy_factory.registry import StrategyRegistry
from modules.operator_dashboard.contracts.strategy_lifecycle import StrategySnapshot


def get_strategy_snapshots(
    *,
    registry: StrategyRegistry,
    confidence_engine=None,
) -> Dict[str, StrategySnapshot]:
    """
    Build an immutable, read-only snapshot of strategy lifecycle state
    for operator dashboards. This function MUST NOT mutate core state.
    """

    snapshots: Dict[str, StrategySnapshot] = {}

    for dna, record in registry.all().items():
        confidence = None

        if confidence_engine is not None:
            result = confidence_engine.compute(dna)
            confidence = result.confidence

        snapshots[dna] = StrategySnapshot(
            dna=dna,
            name=record.spec.name,
            alpha_stream=record.spec.alpha_stream,
            state=record.state,
            execution_status=getattr(record, "execution_status", None),
            ssr=getattr(record, "ssr", None),
            confidence=confidence,
            # Deterministic, non-mutating timestamp
            last_updated=getattr(
                record,
                "last_updated",
                datetime.fromtimestamp(0, tz=timezone.utc),
            ),
        )

    return snapshots
