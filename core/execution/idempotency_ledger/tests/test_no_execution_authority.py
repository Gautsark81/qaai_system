import inspect

from core.execution.idempotency_ledger.ledger import ExecutionIdempotencyLedger


def test_ledger_has_no_execution_methods():
    forbidden = {"execute", "send", "place", "broker", "order"}

    methods = inspect.getmembers(
        ExecutionIdempotencyLedger, predicate=inspect.isfunction
    )

    for name, _ in methods:
        for word in forbidden:
            assert word not in name.lower()
