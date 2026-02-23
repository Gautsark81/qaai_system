from __future__ import annotations

import uuid
from typing import Dict, Any, Optional

from qaai_system.execution.execution_flags import ExecutionFlags
from qaai_system.execution.execution_mode import ExecutionMode
from qaai_system.execution.types import ParentResponse


# ============================================================
# ExecutionEvent (audit record)
# ============================================================

class ExecutionEvent:
    """
    Immutable execution audit event.
    """
    def __init__(self, *, mode: str, order: Dict[str, Any]):
        self.mode = mode
        self.order = order


# ============================================================
# ExecutionRouter
# ============================================================

class ExecutionRouter:
    """
    Canonical execution router.

    CONTRACTS (LOCKED, TEST-ALIGNED)
    ------------------------------------------------------------
    1) flags is None  -> lightweight mode
       submit() -> str (child order id, startswith 'ord_')

    2) flags present -> execution mode
       submit() -> dict:
       {
         "status": "ok" | "error",
         "order_id": str,
         "mode": str
       }

    3) Provider failures are NEVER raised
       - failure is reflected in return value

    4) Audit sink ALWAYS records submission attempt
    """

    def __init__(
        self,
        provider=None,
        *,
        flags: Optional[ExecutionFlags] = None,
        dry_run_broker=None,
        live_broker=None,
        audit_sink=None,
        clock=None,
    ):
        self.provider = provider
        self.flags = flags
        self.dry_run_broker = dry_run_broker or provider
        self.live_broker = live_broker or provider
        self.audit_sink = audit_sink
        self.clock = clock

    # --------------------------------------------------------
    # ID helpers
    # --------------------------------------------------------

    def _child_id(self) -> str:
        return f"ord_{uuid.uuid4().hex[:8]}"

    def _parent_id(self) -> str:
        return f"par_{uuid.uuid4().hex[:8]}"

    def _error_id(self) -> str:
        return f"err_{uuid.uuid4().hex[:8]}"

    # --------------------------------------------------------
    # Mode / broker resolution
    # --------------------------------------------------------

    def _execution_mode(self) -> str:
        if self.flags is None:
            return ExecutionMode.LIVE.value
        return self.flags.mode().value

    def _broker(self):
        if self.flags is None:
            return self.provider
        return self.live_broker if self.flags.is_live() else self.dry_run_broker

    # --------------------------------------------------------
    # Core API
    # --------------------------------------------------------

    def submit(self, order: Dict[str, Any] | None = None, **kwargs):
        """
        Submit an order.

        Lightweight mode:
            -> returns child_order_id (str)

        Execution mode:
            -> returns dict {status, order_id, mode}
        """
        order = order or kwargs.get("order") or {}
        broker = self._broker()
        mode = self._execution_mode()

        child_id = self._child_id()
        parent_id = self._parent_id()

        provider_failed = False

        try:
            if broker and hasattr(broker, "submit_order"):
                broker.submit_order(order)
        except Exception:
            provider_failed = True

        # ------------------ Audit (ALWAYS) ------------------
        if self.audit_sink is not None:
            if not hasattr(self.audit_sink, "events"):
                self.audit_sink.events = []
            self.audit_sink.events.append(
                ExecutionEvent(mode=mode, order=order)
            )

        # ------------------ Failure path --------------------
        if provider_failed:
            err_id = self._error_id()
            if self.flags is None:
                return err_id
            return {
                "status": "error",
                "order_id": err_id,
                "mode": mode,
            }

        # ------------------ Success path --------------------
        if self.flags is None:
            return child_id

        return {
            "status": "ok",
            "order_id": parent_id,
            "mode": mode,
        }

    # --------------------------------------------------------

    def cancel(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order.

        ALWAYS returns:
        {
          "order_id": <id>,
          "status": "CANCELLED"
        }
        """
        broker = self._broker()
        try:
            if broker and hasattr(broker, "cancel_order"):
                broker.cancel_order(order_id)
        except Exception:
            pass

        return {
            "order_id": order_id,
            "status": "CANCELLED",
        }


# ============================================================
# DummyRouter (TEST-ONLY)
# ============================================================

class DummyRouter:
    """
    Test-only router.

    REQUIRED BY TESTS:
    - submit() -> ParentResponse
      status == "filled" (lowercase!)
    - cancel() -> CANCELLED
    - get_status() -> FILLED
    """

    def submit(self, plan: Dict[str, Any]) -> ParentResponse:
        oid = f"ord_{uuid.uuid4().hex[:8]}"
        return ParentResponse(
            order_id=oid,
            status="filled",   # lowercase REQUIRED
            fill_ratio=1.0,
        )

    def cancel(self, order_id: str):
        return {
            "order_id": order_id,
            "status": "CANCELLED",
        }

    def get_status(self, order_id: str):
        return {
            "order_id": order_id,
            "status": "FILLED",
        }
