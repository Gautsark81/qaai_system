# tests/test_order_manager_metrics.py
import pytest
import time
from clients.dhan_safe_client import MockDhanSafeClient
from clients.order_manager import OrderManager
from clients import metrics

class FailAlwaysClient(MockDhanSafeClient):
    def place_order(self, *args, **kwargs):
        raise RuntimeError("permanent failure")

def reset_counter(counter):
    # Prometheus Counter stores value in private _value; set to 0 for tests
    try:
        counter._value.set(0)
    except Exception:
        # fallback: no-op
        pass

def get_value(counter):
    try:
        return float(counter._value.get())
    except Exception:
        return 0.0

def test_orders_placed_increment_on_success():
    client = MockDhanSafeClient()
    om = OrderManager(client)
    # reset metric
    reset_counter(metrics.orders_placed)
    before = get_value(metrics.orders_placed)
    om.place_order("TST", "BUY", qty=1, price=10.0, idempotency_key="m1")
    after = get_value(metrics.orders_placed)
    assert after - before == 1.0

def test_orders_failed_increment_on_permanent_failure():
    client = FailAlwaysClient()
    om = OrderManager(client, max_retries=1, backoff_base=0.001)
    # reset metric
    reset_counter(metrics.orders_failed)
    before = get_value(metrics.orders_failed)
    with pytest.raises(RuntimeError):
        om.place_order("TST", "BUY", qty=1, price=10.0, idempotency_key="m2")
    after = get_value(metrics.orders_failed)
    assert after - before == 1.0
