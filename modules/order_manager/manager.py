# modules/order_manager/manager.py

from datetime import datetime

from modules.execution.plan import ExecutionPlan
from modules.brokers.interface import Broker
from modules.order_manager.ledger import PlanLedger
from modules.runtime.mode import TradingMode
from modules.audit.events import AuditEvent
from modules.audit.sink import AuditSink


_AUDIT = AuditSink()


class OrderManager:
    """
    Exactly-once order submission layer with live-ops safety.

    Guarantees:
    - Idempotent per plan_id
    - Restart-safe via persistent ledger
    - Broker calls gated by runtime trading mode abstraction
    """

    def __init__(self, *, broker: Broker, ledger: PlanLedger):
        self._broker = broker
        self._ledger = ledger

    def submit(self, plan: ExecutionPlan) -> str:
        """
        Submit an execution plan exactly once.

        Safe under:
        - retries
        - crashes
        - restarts
        """
        # Idempotency first (ledger is authoritative)
        existing = self._ledger.get(plan.plan_id)
        if existing is not None:
            _AUDIT.emit(
                AuditEvent(
                    timestamp=datetime.utcnow(),
                    category="ORDER_SKIPPED",
                    entity_id=plan.plan_id,
                    message="Duplicate plan_id skipped",
                )
            )
            return existing

        # Live-ops hard gate (single choke point)
        TradingMode.assert_can_trade()

        # Side-effectful broker call (isolated)
        order = self._broker.submit_market_order(
            symbol=plan.symbol,
            side=plan.side,
            quantity=plan.quantity,
            client_order_id=plan.plan_id,
        )

        # Persist before returning
        self._ledger.record(plan.plan_id, order.broker_order_id)

        _AUDIT.emit(
            AuditEvent(
                timestamp=datetime.utcnow(),
                category="ORDER_SUBMITTED",
                entity_id=plan.plan_id,
                message=f"Broker order {order.broker_order_id} submitted",
            )
        )

        return order.broker_order_id
