from datetime import datetime, timedelta

from qaai_system.model_ops.decay_detection import DecayDecision
from qaai_system.model_ops.orchestration import DecayRollbackBridge


# -----------------------
# Test infrastructure
# -----------------------

class DummyGovernor:
    def __init__(self):
        self.calls = []

    def evaluate(self, *, model_id, metrics):
        self.calls.append((model_id, metrics))


class DummyAuditSink:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


class DummyClock:
    def __init__(self):
        self._now = datetime(2024, 1, 1)

    def utcnow(self):
        return self._now

    def advance(self, delta):
        self._now += delta


class DummyMetrics:
    pass


# -----------------------
# Tests
# -----------------------

def test_no_decay_does_not_trigger_governor():
    governor = DummyGovernor()
    audit = DummyAuditSink()
    clock = DummyClock()

    bridge = DecayRollbackBridge(
        governor=governor,
        audit_sink=audit,
        clock=clock,
        cooldown=timedelta(minutes=10),
    )

    bridge.on_decay(
        model_id="m1",
        decay_decision=DecayDecision(decaying=False, reasons=[]),
        metrics=DummyMetrics(),
    )

    assert governor.calls == []
    assert audit.events[-1].triggered is False


def test_decay_triggers_governor_once():
    governor = DummyGovernor()
    audit = DummyAuditSink()
    clock = DummyClock()

    bridge = DecayRollbackBridge(
        governor=governor,
        audit_sink=audit,
        clock=clock,
        cooldown=timedelta(minutes=10),
    )

    decision = DecayDecision(decaying=True, reasons=["SharpeDecayDetector"])

    bridge.on_decay(
        model_id="m1",
        decay_decision=decision,
        metrics=DummyMetrics(),
    )

    assert len(governor.calls) == 1
    assert audit.events[-1].triggered is True


def test_cooldown_blocks_repeated_triggers():
    governor = DummyGovernor()
    audit = DummyAuditSink()
    clock = DummyClock()

    bridge = DecayRollbackBridge(
        governor=governor,
        audit_sink=audit,
        clock=clock,
        cooldown=timedelta(minutes=10),
    )

    decision = DecayDecision(decaying=True, reasons=["DriftDetector"])

    bridge.on_decay(
        model_id="m1",
        decay_decision=decision,
        metrics=DummyMetrics(),
    )

    # Advance less than cooldown
    clock.advance(timedelta(minutes=5))

    bridge.on_decay(
        model_id="m1",
        decay_decision=decision,
        metrics=DummyMetrics(),
    )

    assert len(governor.calls) == 1  # still only once
    assert audit.events[-1].triggered is False


def test_trigger_after_cooldown_expires():
    governor = DummyGovernor()
    audit = DummyAuditSink()
    clock = DummyClock()

    bridge = DecayRollbackBridge(
        governor=governor,
        audit_sink=audit,
        clock=clock,
        cooldown=timedelta(minutes=10),
    )

    decision = DecayDecision(decaying=True, reasons=["EntropyExplosionDetector"])

    bridge.on_decay(
        model_id="m1",
        decay_decision=decision,
        metrics=DummyMetrics(),
    )

    clock.advance(timedelta(minutes=11))

    bridge.on_decay(
        model_id="m1",
        decay_decision=decision,
        metrics=DummyMetrics(),
    )

    assert len(governor.calls) == 2
