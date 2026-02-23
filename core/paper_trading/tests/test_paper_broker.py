from core.paper_trading.broker import PaperBroker, PaperOrder


def test_paper_broker_fills_order():
    broker = PaperBroker()
    order = PaperOrder("1", "NIFTY", 1, "BUY", 100.0)

    result = broker.place_order(order)
    assert result["status"] == "FILLED"
