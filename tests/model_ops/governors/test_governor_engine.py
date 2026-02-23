from datetime import datetime

from qaai_system.model_ops.governors import (
    RollbackGovernor,
    RollbackMetrics,
    MaxDrawdownRule,
    HardKillDecay,
)


# -----------------------
# Test infrastructure
# -----------------------

class DummyAllocation:
    def __init__(self, weight):
        self.weight = weight


class DummyAllocator:
    def __init__(self):
        self.allocations = {"m1": DummyAllocation(0.5)}

    def get(self, model_id):
        return self.allocations[model_id]


class DummyAuditSink:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


class DummyClock:
    def utcnow(self):
        return datetime(2024, 1, 1)


def test_governor_triggers_and_kills_capital():
    allocator = DummyAllocator()
    audit_sink = DummyAuditSink()

    governor = RollbackGovernor(
        rules=[MaxDrawdownRule(limit=0.2)],
        decay_policy=HardKillDecay(),
        allocator=allocator,
        audit_sink=audit_sink,
        clock=DummyClock(),
    )

    metrics = RollbackMetrics(
        max_drawdown=0.4,
        es_95=0.1,
        sharpe=0.5,
        latency_p99_ms=100,
        error_rate=0.0,
    )

    decision = governor.evaluate(model_id="m1", metrics=metrics)

    assert decision.triggered is True
    assert allocator.get("m1").weight == 0.0
    assert len(audit_sink.events) == 1
