from core.live_trading.promotion import CanaryPromotionEngine, CanaryPolicy
from core.live_trading.audit import AuditLogStore
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.lifecycle import promote


def _live_strategy():
    registry = StrategyRegistry()
    spec = StrategySpec(
        name="audit_test",
        alpha_stream="alpha",
        timeframe="5m",
        universe=["NIFTY"],
        params={},
    )
    record = registry.register(spec)
    promote(record, "BACKTESTED")
    promote(record, "PAPER")
    promote(record, "LIVE")
    return registry, record


def test_audit_event_emitted_on_freeze():
    registry, record = _live_strategy()
    audit_log = AuditLogStore()
    alerts = []

    engine = CanaryPromotionEngine(
        registry=registry,
        policy=CanaryPolicy(max_divergence=1.0, max_slippage=0.1),
        audit_log=audit_log,
        alerts=alerts,
    )

    engine.evaluate(
        dna=record.dna,
        divergence_score=0.0,
        avg_slippage=0.5,
    )

    assert len(audit_log.all()) == 1
    assert audit_log.all()[0].event_type == "CANARY_FREEZE"
    assert len(alerts) == 1
