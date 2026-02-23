from typing import Dict


class BrokerReconciler:
    """
    Compares broker state vs ledger.
    No corrections here — detection only.
    """

    @staticmethod
    def reconcile(
        broker_orders: Dict[str, str],
        ledger_orders: Dict[str, str],
    ) -> Dict[str, str]:
        """
        Returns discrepancies: intent_id -> issue
        """
        issues = {}
        for intent_id, oid in ledger_orders.items():
            if intent_id not in broker_orders:
                issues[intent_id] = "Missing at broker"
        return issues
