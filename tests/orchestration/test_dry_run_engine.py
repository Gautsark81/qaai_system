from datetime import datetime

from qaai_system.orchestration import DryRunOrchestrator, DryRunBroker


class DummyStrategy:
    def generate(self, market_event):
        return {"action": "BUY"}


class DummyExecutionEngine:
    def create_order(self, *, model_id, signal):
        return {
            "model_id": model_id,
            "signal": signal,
        }


class DummyAuditSink:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


class DummyClock:
    def utcnow(self):
        return datetime(2024, 1, 1)


def test_full_dry_run_pipeline():
    audit = DummyAuditSink()

    orchestrator = DryRunOrchestrator(
        strategy_engine=DummyStrategy(),
        execution_engine=DummyExecutionEngine(),
        broker=DryRunBroker(),
        audit_sink=audit,
        clock=DummyClock(),
    )

    result = orchestrator.on_market_event(
        model_id="m1",
        market_event={"price": 100},
    )

    assert result["status"] == "dropped"
    assert len(audit.events) == 1
    assert audit.events[0].action == "order_dropped"
