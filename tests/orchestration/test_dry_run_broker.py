from qaai_system.orchestration import DryRunBroker


def test_dry_run_broker_drops_orders():
    broker = DryRunBroker()

    order = {"symbol": "NIFTY", "qty": 10}
    result = broker.submit_order(order)

    assert result["status"] == "dropped"
    assert len(broker.orders) == 1
