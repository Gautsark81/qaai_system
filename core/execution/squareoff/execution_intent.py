from dataclasses import dataclass

from core.execution.execution_intent import ExecutionIntent


@dataclass(frozen=True, init=False)
class SquareOffExecutionIntent(ExecutionIntent):
    """
    Execution-level intent emitted during square-off.

    Execution governance requires:
    - symbol
    - qty
    - reason
    - audit_id
    """

    symbol: str
    qty: int
    reason: str
    audit_id: str

    def __init__(
        self,
        *,
        symbol: str,
        qty: int,
        reason: str,
        audit_id: str,
    ):
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "qty", qty)
        object.__setattr__(self, "reason", reason)
        object.__setattr__(self, "audit_id", audit_id)
