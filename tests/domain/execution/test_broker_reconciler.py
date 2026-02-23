from domain.execution.broker_reconciler import BrokerReconciler


def test_missing_broker_order_detected():
    broker = {}
    ledger = {"i1": "o1"}
    issues = BrokerReconciler.reconcile(broker, ledger)
    assert "i1" in issues
