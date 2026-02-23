from datetime import datetime
from typing import Any, Dict, List

from core.execution.shadow_executor import ShadowExecutor
from core.execution.shadow_fill_policy import always_fill
from core.execution.shadow_telemetry import build_shadow_telemetry
from core.execution.telemetry import ExecutionEvent, ExecutionTelemetry


class ReferenceShadowExecutor(ShadowExecutor):
    """
    Broker-agnostic, deterministic shadow executor.

    - Never places live orders
    - Always emits execution telemetry
    """

    def __init__(self, execution_id: str):
        self.execution_id = execution_id
        self._events: List[ExecutionEvent] = []

    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        ts = datetime.utcnow()

        # Event: order submitted
        self._events.append(
            ExecutionEvent(
                timestamp=ts,
                event_type="ORDER_SUBMITTED",
                message=f"Order submitted: {order}",
            )
        )

        fill = always_fill(order)

        # Event: order filled
        self._events.append(
            ExecutionEvent(
                timestamp=datetime.utcnow(),
                event_type="ORDER_FILLED",
                message=(
                    f"Filled {fill.filled_qty} @ {fill.price} "
                    f"({fill.reason})"
                ),
            )
        )

        return {
            "status": fill.status,
            "filled_qty": fill.filled_qty,
            "price": fill.price,
            "reason": fill.reason,
        }

    def finalize(self) -> ExecutionTelemetry:
        """
        Finalize execution and emit telemetry snapshot.
        """
        # Event: execution completed
        self._events.append(
            ExecutionEvent(
                timestamp=datetime.utcnow(),
                event_type="EXECUTION_COMPLETED",
                message="Shadow execution completed",
            )
        )

        return build_shadow_telemetry(
            execution_id=self.execution_id,
            events=tuple(self._events),
            total_orders=1,
            filled_orders=1,
            rejected_orders=0,
            cancelled_orders=0,
        )
