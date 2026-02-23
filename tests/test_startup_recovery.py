# tests/test_startup_recovery.py
import time
from clients.sqlite_order_cache import SqliteOrderCache
from clients.order_manager import OrderManager
from clients.order_reconciler import OrderReconciler
from clients.dhan_safe_client import MockDhanSafeClient

class MockClientForReconcile(MockDhanSafeClient):
    def __init__(self, status_map):
        super().__init__()
        self.status_map = status_map

    def get_order_status(self, order_id):
        # return a mapping that sets status to the mapped value, else NEW
        return {"status": self.status_map.get(order_id, "NEW")}

def test_reconciler_run_once_updates_persistent_cache(tmp_path):
    db = str(tmp_path / "orders.db")
    cache = SqliteOrderCache(db)
    # seed an order as persisted with status NEW
    order_id = "ord-001"
    cache.save_order(order_id, {"order_id": order_id, "symbol": "TST", "status": "NEW", "created_at": time.time()})
    # client will report the order as FILLED
    client = MockClientForReconcile({order_id: "FILLED"})
    om = OrderManager(client, persistent_order_store=cache)
    reconciler = OrderReconciler(om, poll_interval=1.0)
    # now run one pass synchronously
    reconciler.run_once()
    # reload cache via new instance and ensure status updated
    cache2 = SqliteOrderCache(db)
    all_orders = cache2.load_all()
    assert order_id in all_orders
    assert all_orders[order_id]["status"].upper() == "FILLED"
    cache.close()
    cache2.close()
