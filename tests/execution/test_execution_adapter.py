from datetime import datetime

from qaai_system.execution.execution_flags import ExecutionFlags
from qaai_system.execution.execution_adapter import ExecutionAdapter
from qaai_system.execution.execution_mode import ExecutionMode


class DummyRouter:
    def __init__(self):
        self.called = False

    def submit(self, plan):
        self.called = True
        return {"status": "submitted", "order_id": "live_1"}


class DummyAudit:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


class DummyClock:
    def utcnow(self):
        return datetime(2024, 1, 1)


def test_dry_run_does_not_call_router():
    router = DummyRouter()
    flags = ExecutionFlags()
    audit = DummyAudit()

    adapter = ExecutionAdapter(
        router=router,
        flags=flags,
        audit_sink=audit,
        clock=DummyClock(),
    )

    result = adapter.submit({"symbol": "NIFTY", "qty": 1})

    assert result["status"] == "dropped"
    assert router.called is False
    assert audit.events[0]["mode"] == ExecutionMode.DRY_RUN.value


def test_live_calls_router():
    router = DummyRouter()
    flags = ExecutionFlags()
    flags.set_live()
    audit = DummyAudit()

    adapter = ExecutionAdapter(
        router=router,
        flags=flags,
        audit_sink=audit,
        clock=DummyClock(),
    )

    result = adapter.submit({"symbol": "NIFTY", "qty": 1})

    assert result["status"] == "submitted"
    assert router.called is True
    assert audit.events[0]["mode"] == ExecutionMode.LIVE.value
