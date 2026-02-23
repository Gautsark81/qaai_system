Phase 2 Quickstart

1) Create TickStore and Mock client:
   from data.tick_store import TickStore
   from clients.dhan_safe_client import MockDhanSafeClient
   from data.strategy import StrategyContext
   from data.registry import StrategyRegistry
   import examples.strategies.simple_mean_reversion  # registers strategy

   ts = TickStore(db_path=":memory:")
   client = MockDhanSafeClient()
   ctx = StrategyContext(ts, client, config={"name":"smr", "window":5, "threshold":0.5})
   reg = StrategyRegistry()
   inst = reg.create("simple_mean_reversion", ctx, "smr-1")
   reg.start("smr-1")

2) In production you'll implement DhanSafeClient.place_order/cancel_order with real API calls.
3) A simple dispatcher should call `inst.on_tick(tick)` for each incoming tick (e.g., from TickStore append or a message bus).
