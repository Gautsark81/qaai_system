from datetime import datetime

from core.v2.paper_trading.execution.execution_engine import ExecutionEngine
from core.v2.paper_trading.execution.paper_broker import PaperBroker
from core.v2.paper_trading.orders.order import PaperOrderRequest
from core.v2.paper_trading.orders.order_book import OrderBook


def test_execution_engine_submits_and_fills():
    def price_provider(symbol, ts):
        return 123.0

    broker = PaperBroker(price_provider=price_provider)
    book = OrderBook()
    engine = ExecutionEngine(broker=broker, order_book=book)

    req = PaperOrderRequest(
        strategy_id="s1",
        symbol="AAPL",
        side="BUY",
        quantity=5,
        created_at=datetime.utcnow(),
    )

    fill = engine.submit(req)

    assert fill.price == 123.0
    assert fill.quantity == 5
    assert len(book.all_orders()) == 1
