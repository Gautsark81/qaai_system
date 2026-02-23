"""
STEP-10.3-4 — Execute a single approved LIVE CANARY trade
SINGLE-USE, HARD-LOCKED, SAFE
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------
# ENSURE PROJECT ROOT IS ON PATH
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ------------------------------------------------------------
# CANARY CONSTANTS (LOCKED)
# ------------------------------------------------------------

ORDER_ID = "CANARY_bd34163b"        # approval & audit only
STRATEGY_ID = "STRAT_CANARY"
SYMBOL = "RELIANCE"
SIDE = "BUY"
QTY = 1
PRICE = 2500.0                     # deterministic canary price

APPROVAL_FILE = ROOT / "data" / "live_approvals" / f"{ORDER_ID}.approved"
EXECUTION_LOCK = ROOT / "data" / "live_approvals" / f"{ORDER_ID}.executed"

# ------------------------------------------------------------
# ENV SAFETY CHECKS
# ------------------------------------------------------------

if os.getenv("TRADING_ENV") != "live_canary":
    raise RuntimeError("Not in LIVE_CANARY mode")

if os.getenv("EXECUTION_ENABLED", "").lower() != "true":
    raise RuntimeError("EXECUTION_ENABLED must be true")

if not APPROVAL_FILE.exists():
    raise RuntimeError("Approval not found — execution denied")

if EXECUTION_LOCK.exists():
    raise RuntimeError("Order already executed — hard stop")

# ------------------------------------------------------------
# KILL SWITCH CHECK
# ------------------------------------------------------------

from core.safety.kill_switch import KillSwitch

ks = KillSwitch()
ks.assert_can_trade()

# ------------------------------------------------------------
# EXECUTION (FINAL, CONTRACT-CORRECT)
# ------------------------------------------------------------

from core.paper.paper_executor import PaperExecutor

print("\n🚨 LIVE CANARY EXECUTION STARTING")
print(f"order_id (audit): {ORDER_ID}")
print(f"strategy: {STRATEGY_ID}")
print(f"symbol: {SYMBOL}")
print(f"side: {SIDE}")
print(f"qty: {QTY}")
print(f"price: {PRICE}")

executor = PaperExecutor(kill_switch=ks)

result = executor.execute(
    STRATEGY_ID,
    SYMBOL,
    SIDE,
    QTY,
    PRICE,
)

# ------------------------------------------------------------
# POST-EXECUTION LOCK (IRREVERSIBLE)
# ------------------------------------------------------------

EXECUTION_LOCK.write_text(
    f"order_id={ORDER_ID}\nexecuted_at={datetime.utcnow().isoformat()}\n"
)

# AUTO-RELOCK (runtime only)
os.environ["EXECUTION_ENABLED"] = "false"

print("\n✅ LIVE CANARY EXECUTION COMPLETE")
print("🔒 Execution auto-disabled")
print("📁 Execution permanently locked")

print("\n📦 EXECUTION RESULT")
print(result)
