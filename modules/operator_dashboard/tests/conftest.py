import pytest

from core.strategy_factory.registry import StrategyRegistry
from core.phase_b.confidence import ConfidenceEngine

from modules.operator_dashboard.service import DashboardService


@pytest.fixture
def snapshot():
    """
    Canonical dashboard snapshot fixture for operator dashboard tests.

    Phase-F guarantees:
    - Read-only
    - Deterministic
    - No mutation of core state
    """

    registry = StrategyRegistry()

    confidence_engine = ConfidenceEngine(registry)

    dashboard = DashboardService(
        registry=registry,
        confidence_engine=confidence_engine,
    )

    return dashboard.build_snapshot()
