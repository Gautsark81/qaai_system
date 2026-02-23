from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class ExecutionPermission:
    """
    Immutable runtime permission allowing execution to proceed.

    This object:
    - Is created AFTER capital allocation + gate evaluation
    - Is REQUIRED by the ExecutionEngine
    - Contains NO decision logic
    - Is safe to persist, replay, and audit
    """

    strategy_id: str
    allowed: bool
    issued_at: datetime

    # Contextual evidence (read-only, optional)
    allocated_capital: Optional[float] = None
    gate_reasons: List[str] = field(default_factory=list)

    def assert_allowed(self) -> None:
        """
        Raises if execution is not permitted.
        ExecutionEngine must call this.
        """
        if not self.allowed:
            raise PermissionError(
                f"Execution denied for strategy {self.strategy_id}: "
                f"{'; '.join(self.gate_reasons)}"
            )
