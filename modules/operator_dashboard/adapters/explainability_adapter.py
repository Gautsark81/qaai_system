from core.explainability.strategy import StrategyExplainer

from modules.operator_dashboard.contracts.dashboard_snapshot import ExplainabilitySnapshot


def get_explainability_snapshot() -> ExplainabilitySnapshot:
    explainer = StrategyExplainer()

    return ExplainabilitySnapshot(
        decisions=explainer.latest_decisions(),
        traces=explainer.latest_traces(),
    )
from core.strategy_factory.registry import StrategyRegistry
from core.explainability.strategy import StrategyExplainer
from modules.operator_dashboard.contracts.explainability import (
    ExplainabilitySnapshot,
)


def get_explainability_snapshot() -> ExplainabilitySnapshot:
    """
    Dashboard-safe explainability projection.
    """

    registry = StrategyRegistry.global_instance()
    explainer = StrategyExplainer(registry)

    return explainer.snapshot()
