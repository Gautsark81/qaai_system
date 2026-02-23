from datetime import datetime

from qaai_system.execution import (
    ExecutionRouter,
    ExecutionFlags,
    ExecutionMode,
)


class DummyBroker:
    def __init__(self):
        self.orders = []

    def submit_order(self, order):
        self.orders.append(order)
        return {"status": "ok", "order": order}


class DummyAudit:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


class DummyClock:
    def utcnow(self):
        return datetime(2024, 1, 1)


def test_dry_run_routing():
    flags = ExecutionFlags()
    dry = DummyBroker()
    audit = DummyAudit()

    router = ExecutionRouter(
        flags=flags,
        dry_run_broker=dry,
        live_broker=None,
        audit_sink=audit,
        clock=DummyClock(),
    )

    result = router.submit(model_id="m1", order={"qty": 1})

    assert result["status"] == "ok"
    assert len(dry.orders) == 1
    assert audit.events[0].mode == ExecutionMode.DRY_RUN.value


def test_live_routing():
    flags = ExecutionFlags()
    flags.set_mode(ExecutionMode.LIVE)

    dry = DummyBroker()
    live = DummyBroker()
    audit = DummyAudit()

    router = ExecutionRouter(
        flags=flags,
        dry_run_broker=dry,
        live_broker=live,
        audit_sink=audit,
        clock=DummyClock(),
    )

    router.submit(model_id="m1", order={"qty": 5})

    assert len(live.orders) == 1
    assert audit.events[0].mode == ExecutionMode.LIVE.value

def test_execution_router_single_entrypoint():
    """
    Guard test: ExecutionRouter must have exactly one canonical definition.
    Any shadow router must fail CI.
    """
    from qaai_system.execution import ExecutionRouter as A
    from qaai_system.execution.router import ExecutionRouter as B

    assert A is B, (
        "ExecutionRouter import mismatch detected. "
        "All execution routing must use qaai_system.execution.router.ExecutionRouter"
    )
