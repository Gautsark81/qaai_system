"""
Cold-start & restart recovery tests.

Hard guarantees:
- Orphan broker orders are cancelled
- Known orders are preserved
- Restart is idempotent
- Execution NEVER starts before validation
"""

import pytest

from modules.execution.recovery.reconciler import BrokerReconciler
from modules.execution.recovery.cold_start_validator import ColdStartValidator


# ==========================================================
# FIXTURES
# ==========================================================

@pytest.fixture
def fake_broker():
    class FakeBroker:
        def __init__(self):
            self._open_orders = []
            self.cancelled = []

        def fetch_open_orders(self):
            return list(self._open_orders)

        def cancel(self, order_id):
            self.cancelled.append(order_id)

    return FakeBroker()


@pytest.fixture
def fake_state_store():
    class FakeStateStore:
        def __init__(self):
            self._open_orders = []

        def load_open_orders(self):
            return list(self._open_orders)

    return FakeStateStore()


# ==========================================================
# TESTS
# ==========================================================

def test_orphan_broker_orders_are_cancelled(fake_broker, fake_state_store):
    fake_broker._open_orders = ["ORD1"]
    fake_state_store._open_orders = []

    reconciler = BrokerReconciler(fake_broker)
    validator = ColdStartValidator(reconciler, fake_state_store)

    validator.validate()

    assert fake_broker.cancelled == ["ORD1"]


def test_known_orders_are_preserved(fake_broker, fake_state_store):
    fake_broker._open_orders = ["ORD1"]
    fake_state_store._open_orders = ["ORD1"]

    reconciler = BrokerReconciler(fake_broker)
    validator = ColdStartValidator(reconciler, fake_state_store)

    validator.validate()

    assert fake_broker.cancelled == []


def test_restart_is_idempotent(fake_broker, fake_state_store):
    fake_broker._open_orders = ["ORD1"]
    fake_state_store._open_orders = []

    reconciler = BrokerReconciler(fake_broker)
    validator = ColdStartValidator(reconciler, fake_state_store)

    validator.validate()
    validator.validate()  # second restart

    assert fake_broker.cancelled == ["ORD1"]


def test_execution_never_starts_before_validation(monkeypatch):
    """
    Execution must NEVER start if recovery fails.
    """

    def fail_validate(self):
        raise SystemExit("Recovery failed")

    monkeypatch.setattr(
        "modules.execution.recovery.cold_start_validator.ColdStartValidator.validate",
        fail_validate,
    )

    start_called = {"flag": False}

    def fake_start(self):
        start_called["flag"] = True

    monkeypatch.setattr(
        "modules.execution.orchestrator.ExecutionOrchestrator.start",
        fake_start,
    )

    import bootstrap

    with pytest.raises(SystemExit):
        bootstrap.bootstrap()

    assert start_called["flag"] is False
