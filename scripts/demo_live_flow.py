# scripts/demo_live_flow.py
import sys
import os

# ensure repo root is on sys.path so top-level module folders (providers, infra, data, etc.) are importable
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from providers.dhan_provider import DhanProvider
from data.ingestion.paper_provider import PaperProvider
from providers.unified_provider import UnifiedProvider
from infra.order_queue import OrderQueue
from infra.heartbeat import Heartbeat
from infra.live_pnl import LivePnL

# setup
paper = PaperProvider(config={"starting_cash": 10000})
dhan = DhanProvider(config={"starting_cash": 10000})
up = UnifiedProvider(paper_provider=paper, live_provider=dhan, default_mode="live")

hb = Heartbeat(provider=up, reconnect_attempts=1)
print("Connected:", hb.check_and_reconnect())

oq = OrderQueue(provider=up, throttle_seconds=0.0)
print(
    "Submit order:",
    oq.submit({"symbol": "TST", "side": "buy", "quantity": 2, "price": 100.0}),
)

lp = LivePnL(provider=up, price_lookup=lambda s: 101.0)
print("PnL snapshot:", lp.get_snapshot())
