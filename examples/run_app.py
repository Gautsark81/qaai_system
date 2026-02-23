# examples/run_app.py
import time
import logging
from data.tick_store import TickStore
from data.registry import StrategyRegistry
from data.strategy import StrategyContext
from clients.dhan_safe_client import MockDhanSafeClient
from clients.order_manager import OrderManager
from clients.async_order_manager import AsyncOrderManager
from clients.idempotency_sqlite import SqliteIdempotencyStore
from clients.order_reconciler import OrderReconciler
from clients.metrics_server import start_metrics_server
from data.dispatcher import AsyncDispatcher
import examples.strategies.simple_mean_reversion  # registers strategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amats")

# inside your app bootstrap, before dispatcher.start():
# assume om is OrderManager and reconciler is OrderReconciler
logger.info("Running startup recovery (reconciler.run_once())")
try:
    reconciler.run_once()  # synchronous pass
    logger.info("Startup reconciliation complete; now starting dispatcher")
except Exception:
    logger.exception("Startup reconciliation failed; continuing but consider aborting in production")
# now safe to start dispatcher & accept ticks/orders
disp.start()

def main():
    # start metrics server
    start_metrics_server(port=8000)
    # prepare stores & clients
    ts = TickStore(db_path=":memory:")
    client = MockDhanSafeClient()
    idemp = SqliteIdempotencyStore("idemp.db")
    om = OrderManager(client, idempotency_store={})
    aom = AsyncOrderManager(om)
    reconciler = OrderReconciler(om, poll_interval=5.0, idempotency_store=idemp)

    # registry + strategy
    reg = StrategyRegistry()
    ctx = StrategyContext(tick_store=ts, order_client=client, order_manager=aom, config={"name": "smr", "window": 3, "threshold": 0.5})
    inst = reg.create("simple_mean_reversion", ctx, instance_id="smr-1")

    # dispatcher that manages reconciler lifecycle
    disp = AsyncDispatcher(registry=reg, reconciler=reconciler)
    disp.start()
    disp.map_symbol_to_instance("SMB", "smr-1", strategy_obj=inst)

    now = time.time()
    try:
        for p in [100.0, 99.0, 101.5, 98.5, 102.0, 97.0]:
            t = {"symbol": "SMB", "timestamp": time.time(), "price": p, "size": 1}
            ts.append_tick("SMB", t)
            disp.submit_tick("SMB", t)
            time.sleep(0.1)
        time.sleep(2.0)
    finally:
        disp.stop()
        reconciler.stop()
        ts.close()
        idemp.close()
        logger.info("Example run complete")

if __name__ == "__main__":
    main()
