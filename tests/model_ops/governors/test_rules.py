from qaai_system.model_ops.governors import (
    RollbackMetrics,
    MaxDrawdownRule,
    ErrorRateRule,
    LatencyRule,
)


def base_metrics(**overrides):
    base = dict(
        max_drawdown=0.1,
        es_95=0.05,
        sharpe=1.0,
        latency_p99_ms=100,
        error_rate=0.0,
    )
    base.update(overrides)
    return RollbackMetrics(**base)


def test_max_drawdown_rule_triggers():
    rule = MaxDrawdownRule(limit=0.2)
    assert rule.evaluate(base_metrics(max_drawdown=0.3)) is True


def test_error_rate_rule_triggers():
    rule = ErrorRateRule()
    assert rule.evaluate(base_metrics(error_rate=0.01)) is True


def test_latency_rule_triggers():
    rule = LatencyRule(limit_ms=200)
    assert rule.evaluate(base_metrics(latency_p99_ms=300)) is True


def test_rules_do_not_trigger_when_safe():
    rules = [
        MaxDrawdownRule(0.5),
        ErrorRateRule(),
        LatencyRule(500),
    ]
    metrics = base_metrics()

    for rule in rules:
        assert rule.evaluate(metrics) is False
