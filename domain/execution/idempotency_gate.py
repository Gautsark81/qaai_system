from domain.execution.execution_intent import ExecutionIntent
from domain.execution.execution_ledger import ExecutionLedger


class IdempotencyGate:
    """
    Prevents duplicate real-world orders.
    """

    @staticmethod
    def allow(intent: ExecutionIntent, ledger: ExecutionLedger) -> bool:
        return not ledger.exists(intent.intent_id())
