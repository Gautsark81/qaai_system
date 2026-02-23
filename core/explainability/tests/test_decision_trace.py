from datetime import datetime

from core.explainability.decision_trace import DecisionTraceExplainer
from core.strategy_factory.registry import StrategyRegistry
from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.lifecycle import promote
from core.live_trading.audit import AuditLogStore, AuditEvent


def test_decision_trace_explains_lifecycle_and_audit():
    registry = StrategyRegistry()
    audit_log = AuditLogStore()

    spec = StrategySpec(
        name="trace_test",
        alpha_stream="alpha_trace",
        timeframe="5m",
        universe=["NIFTY"],
        params={"x": 1},
    )

    record = registry.register(spec)
    promote(record, "BACKTESTED")
    promote(record, "PAPER")

    # ✅ FULL canonical AuditEvent
    audit_log.append(
        AuditEvent(
            dna=record.dna,
            event_type="CANARY_FREEZE",
            timestamp=datetime.utcnow(),
            payload={
                "source": "canary",
                "note": "slippage breach",
            },
        )
    )

    explainer = DecisionTraceExplainer(
        registry=registry,
        audit_log=audit_log,
    )

    explanation = explainer.explain(record.dna)

    lifecycle = explanation["decision_trace"]["lifecycle"]
    audit = explanation["decision_trace"]["audit"]

    assert lifecycle["type"] == "LIFECYCLE"
    assert audit["type"] == "AUDIT"
    assert audit["event_type"] == "CANARY_FREEZE"
    assert "frozen" in audit["explanation"].lower()
