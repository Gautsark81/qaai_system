# run_dispatcher_example.py
import time
from data.tick_store import TickStore
from clients.dhan_safe_client import MockDhanSafeClient
from data.registry import StrategyRegistry
from data.strategy import StrategyContext
from data.dispatcher import AsyncDispatcher
import examples.strategies.simple_mean_reversion  # registers the strategy

ts = TickStore(db_path=":memory:")
client = MockDhanSafeClient()
reg = StrategyRegistry()
ctx = StrategyContext(tick_store=ts, order_client=client, config={"name": "smr", "window": 3, "threshold": 0.01})
inst = reg.create("simple_mean_reversion", ctx, instance_id="smr-1")

disp = AsyncDispatcher(registry=reg)
disp.start()
disp.map_symbol_to_instance("SMB", "smr-1", strategy_obj=inst)

now = time.time()
for p in [100.0, 99.0, 101.5, 98.5, 102.0]:
    t = {"symbol": "SMB", "timestamp": time.time(), "price": p, "size": 1}
    ts.append_tick("SMB", t)  # keep tick store in sync with dispatcher usage
    disp.submit_tick("SMB", t)
    time.sleep(0.05)

time.sleep(1.0)  # allow processing
disp.stop()
ts.close()
print("orders placed:", len(client._orders))
