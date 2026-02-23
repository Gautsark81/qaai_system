from datetime import datetime, time

import pytest

from qaai_system.model_ops.retraining import (
    RetrainingDecision,
    RetrainingPlan,
    MarketRegime,
)
from qaai_system.model_ops.retraining.orchestrator import (
    ShadowRetrainingOrchestrator,
)
from qaai_system.model_ops.retraining.errors import RetrainingError


# -----------------------
# Test infrastructure
# -----------------------

class DummyQueue:
    def __init__(self):
        self.jobs = []

    def enqueue(self, job):
        self.jobs.append(job)


class DummyAudit:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


class DummyClock:
    def __init__(self, now):
        self._now = now

    def utcnow(self):
        return self._now


def make_plan():
    return RetrainingPlan(
        regime=MarketRegime.HIGH_VOL,
        lookback_days=120,
        model_family="gbt",
        featureset="v2",
        reasons=["decay"],
    )


# -----------------------
# Tests
# -----------------------

def test_schedule_shadow_training_job():
    queue = DummyQueue()
    audit = DummyAudit()
    clock = DummyClock(datetime(2024, 1, 1, 20, 0))  # after market

    orchestrator = ShadowRetrainingOrchestrator(
        training_queue=queue,
        audit_sink=audit,
        clock=clock,
    )

    decision = RetrainingDecision(True, ["decay"], MarketRegime.HIGH_VOL)
    plan = make_plan()

    job = orchestrator.schedule(
        model_id="m1",
        decision=decision,
        plan=plan,
    )

    assert job is not None
    assert len(queue.jobs) == 1
    assert job.model_id == "m1"


def test_idempotent_job_submission():
    queue = DummyQueue()
    audit = DummyAudit()
    clock = DummyClock(datetime(2024, 1, 1, 20, 0))

    orchestrator = ShadowRetrainingOrchestrator(
        training_queue=queue,
        audit_sink=audit,
        clock=clock,
    )

    decision = RetrainingDecision(True, ["decay"], MarketRegime.HIGH_VOL)
    plan = make_plan()

    orchestrator.schedule("m1", decision, plan)
    orchestrator.schedule("m1", decision, plan)

    assert len(queue.jobs) == 1


def test_retraining_blocked_during_market_hours():
    queue = DummyQueue()
    audit = DummyAudit()
    clock = DummyClock(datetime(2024, 1, 1, 10, 0))  # market open

    orchestrator = ShadowRetrainingOrchestrator(
        training_queue=queue,
        audit_sink=audit,
        clock=clock,
    )

    decision = RetrainingDecision(True, ["decay"], MarketRegime.HIGH_VOL)
    plan = make_plan()

    with pytest.raises(RetrainingError):
        orchestrator.schedule("m1", decision, plan)
