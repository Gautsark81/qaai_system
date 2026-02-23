from domain.execution.execution_intent import ExecutionIntent
from domain.execution.execution_ledger import ExecutionLedger
from domain.execution.idempotency_gate import IdempotencyGate


class SafeExecutor:
    """
    Wraps execution with idempotency.
    """

    def __init__(self, ledger: ExecutionLedger):
        self.ledger = ledger

    def submit(self, intent: ExecutionIntent, submit_fn) -> str:
        """
        submit_fn: callable returning broker_order_id
        """
        if not IdempotencyGate.allow(intent, self.ledger):
            return self.ledger.get(intent.intent_id())

        broker_order_id = submit_fn(intent)
        self.ledger.record(intent.intent_id(), broker_order_id)
        return broker_order_id
