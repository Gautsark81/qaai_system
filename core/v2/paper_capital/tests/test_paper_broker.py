from datetime import datetime

from core.v2.paper_trading.contracts import PaperOrder
from core.v2.paper_trading.execution.paper_broker import PaperBroker


def test_paper_broker_executes_deterministically():
    def price_provider(symbol, ts):
        return 100.0

    broker = PaperBroker(price_provider=price_provider)

    order = PaperOrder(
        order_id="o1",
        strategy_id="s1",
        symbol="AAPL",
        side="BUY",
        quantity=10,
        created_at=datetime.utcnow(),
    )

    fill = broker.execute(order)

    assert fill.price == 100.0
    assert fill.quantity == 10
    assert fill.order_id == "o1"
