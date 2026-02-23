# tests/test_order_cache_persistence.py
import tempfile
import os
from clients.sqlite_order_cache import SqliteOrderCache
from clients.order_manager import OrderManager
from clients.dhan_safe_client import MockDhanSafeClient

def test_sqlite_order_cache_roundtrip(tmp_path):
    db = str(tmp_path / "orders.db")
    cache = SqliteOrderCache(db)
    # create a fake metadata and save
    oid = "o-123"
    meta = {"order_id": oid, "symbol": "TST", "status": "NEW"}
    cache.save_order(oid, meta)
    # load via new instance
    cache2 = SqliteOrderCache(db)
    all_orders = cache2.load_all()
    assert oid in all_orders
    assert all_orders[oid]["symbol"] == "TST"
    cache.close()
    cache2.close()

def test_order_manager_loads_persisted_orders(tmp_path):
    db = str(tmp_path / "orders2.db")
    cache = SqliteOrderCache(db)
    # prepare some persisted orders
    cache.save_order("o1", {"order_id": "o1", "symbol": "S", "status": "NEW"})
    # create an OrderManager with persistent store and ensure it loads
    client = MockDhanSafeClient()
    om = OrderManager(client, persistent_order_store=cache)
    local = om.list_local_orders()
    assert "o1" in local
    cache.close()
