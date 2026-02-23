from datetime import datetime
from typing import Any, Dict

from qaai_system.execution.execution_mode import ExecutionMode
from qaai_system.execution.execution_flags import ExecutionFlags


class ExecutionAdapter:
    """
    Feature-flagged adapter around existing OrderRouter.

    - DRY_RUN: plans are evaluated, risk checked, but orders are dropped
    - LIVE: full OrderRouter.submit() path is executed
    """

    def __init__(
        self,
        *,
        router,          # your existing OrderRouter instance
        flags: ExecutionFlags,
        audit_sink,
        clock,
    ):
        self.router = router
        self.flags = flags
        self.audit_sink = audit_sink
        self.clock = clock

    def submit(self, plan: Dict[str, Any]):
        mode = self.flags.mode()

        if mode == ExecutionMode.DRY_RUN:
            # IMPORTANT:
            # We DO NOT call router.submit()
            # This guarantees zero broker interaction
            result = {
                "status": "dropped",
                "reason": "dry_run",
                "plan": plan,
            }
        else:
            # LIVE path — full router logic
            result = self.router.submit(plan)

        # Audit both paths
        self.audit_sink.emit(
            {
                "event": "execution_attempt",
                "mode": mode.value,
                "symbol": plan.get("symbol"),
                "status": result.get("status") if isinstance(result, dict) else "submitted",
                "timestamp": self.clock.utcnow(),
            }
        )

        return result
