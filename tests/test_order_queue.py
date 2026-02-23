# tests/test_order_queue.py
from infra.order_queue import OrderQueue
from providers.dhan_provider import DhanProvider


def test_order_queue_basic(tmp_path):
    dp = DhanProvider(config={"starting_cash": 1000})
    dp.connect()
    oq = OrderQueue(provider=dp, throttle_seconds=0.0, max_retries=0, retry_delay=0.0)
    resp = oq.submit({"symbol": "X", "side": "buy", "quantity": 1, "price": 10.0})
    assert resp.get("status") == "filled"
