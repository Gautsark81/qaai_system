from domain.broker.broker_position_snapshot import BrokerPositionSnapshot
from domain.canary.system_position_record import SystemPositionRecord
from domain.canary.position_reconciliation_result import (
    PositionReconciliationResult
)


class PositionReconciler:
    """
    Compares system vs broker holdings.
    """

    @staticmethod
    def reconcile(
        system: SystemPositionRecord,
        broker: BrokerPositionSnapshot,
    ) -> PositionReconciliationResult:

        delta = broker.quantity - system.quantity
        matched = delta == 0

        return PositionReconciliationResult(
            symbol=system.symbol,
            system_qty=system.quantity,
            broker_qty=broker.quantity,
            delta_qty=delta,
            matched=matched,
        )
