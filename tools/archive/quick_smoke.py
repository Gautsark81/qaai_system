# quick_smoke.py
from data.tick_store import TickStore
import time

ts = TickStore(db_path=":memory:")
ts.append_tick("ABC", {"timestamp": time.time(), "price": 123.45, "size": 1})
print(ts.get_latest("ABC"))
print(ts.snapshot("ABC"))
ts.close()
