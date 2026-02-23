# tools/startup_recovery.py
"""
Run reconciler once at startup to recover persisted orders before starting live trading.
Example usage:
    python tools/startup_recovery.py
"""

from __future__ import annotations
import logging
import time
from clients.order_manager import OrderManager
from clients.sqlite_order_cache import SqliteOrderCache
from clients.order_reconciler import OrderReconciler
from clients.dhan_safe_client import MockDhanSafeClient  # use real client in production

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("startup_recovery")

def main():
    # persistent order store (file)
    order_cache = SqliteOrderCache("startup_orders.db")
    # idempotency store (sqlite)
    from clients.idempotency_sqlite import SqliteIdempotencyStore
    idemp = SqliteIdempotencyStore(":memory:")

    client = MockDhanSafeClient()
    om = OrderManager(client, idempotency_store=idemp, persistent_order_store=order_cache)
    reconciler = OrderReconciler(om, poll_interval=5.0, idempotency_store=idemp)

    # run one reconciliation pass synchronously
    reconciler.run_once()

    logger.info("Startup recovery completed")
    # continue with starting dispatcher or other services...
    # (this script exits; integrate its logic into your app boot sequence)

if __name__ == "__main__":
    main()
