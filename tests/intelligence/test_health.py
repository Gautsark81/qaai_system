from modules.intelligence.health import StrategyHealthEvaluator, StrategyHealth
from modules.intelligence.metrics import StrategyMetrics


def test_health_healthy():
    metrics = StrategyMetrics(50, 30, 20, 1200)
    report = StrategyHealthEvaluator().evaluate(metrics)
    assert report.health == StrategyHealth.HEALTHY


def test_health_degraded():
    metrics = StrategyMetrics(10, 6, 4, 200)
    report = StrategyHealthEvaluator().evaluate(metrics)
    assert report.health == StrategyHealth.DEGRADED
