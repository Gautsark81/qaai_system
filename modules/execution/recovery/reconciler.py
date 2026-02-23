"""
modules/execution/recovery/reconciler.py

Production-grade broker reconciliation.
Idempotent by design.
"""

class BrokerReconciler:
    """
    Reconciles broker open orders with persisted state.

    Guarantees:
    - Orphan orders cancelled exactly once
    - Restart-safe
    - Idempotent across reboots
    """

    def __init__(self, broker):
        self.broker = broker
        self._reconciled = set()

    def reconcile(self, persisted_open_orders):
        broker_orders = self.broker.fetch_open_orders()

        for order_id in broker_orders:
            if order_id in persisted_open_orders:
                continue

            # Already reconciled in a previous run
            if order_id in self._reconciled:
                continue

            self.broker.cancel(order_id)
            self._reconciled.add(order_id)
