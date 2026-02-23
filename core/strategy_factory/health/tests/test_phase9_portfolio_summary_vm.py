from core.strategy_factory.health.dashboard.dashboard_view_models import (
    PortfolioSummaryVM,
)
from core.strategy_factory.health.strategy_health_report import StrategyHealthStatus


class DummyAggregator:
    total_strategies = 3
    status_counts = {
        StrategyHealthStatus.HEALTHY: 2,
        StrategyHealthStatus.DEGRADED: 1,
    }
    overall_status = StrategyHealthStatus.HEALTHY
    promotion_pressure = False
    demotion_pressure = False


def test_portfolio_summary_vm_from_aggregator():
    vm = PortfolioSummaryVM.from_aggregator(DummyAggregator())

    assert vm.total_strategies == 3
    assert vm.overall_health == StrategyHealthStatus.HEALTHY
    assert vm.counts[StrategyHealthStatus.DEGRADED] == 1
