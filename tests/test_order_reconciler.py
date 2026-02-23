# tests/test_order_reconciler.py
import time
import tempfile
import os
from clients.dhan_safe_client import MockDhanSafeClient
from clients.order_manager import OrderManager
from clients.idempotency_sqlite import SqliteIdempotencyStore
from clients.order_reconciler import OrderReconciler

def test_reconciler_persists_idempotency(tmp_path):
    client = MockDhanSafeClient()
    # create sqlite idempotency store on disk
    db_path = str(tmp_path / "idemp.db")
    store = SqliteIdempotencyStore(db_path)
    om = OrderManager(client, idempotency_store={})
    # place an order and ensure idempotency key stored in manager
    meta = om.place_order("T", "BUY", qty=1, price=1.0, idempotency_key="recon-1")
    oid = meta["order_id"]
    # create reconciler that will persist persisted mapping to store
    reconciler = OrderReconciler(om, poll_interval=0.1, lookback_seconds=60, idempotency_store=store)
    reconciler.start()
    # wait a little for reconciler to run at least once
    time.sleep(0.3)
    # check that idempotency key was persisted
    persisted = store.get("recon-1")
    assert isinstance(persisted, dict)
    assert persisted.get("order_id") == oid
    reconciler.stop()
    store.close()
