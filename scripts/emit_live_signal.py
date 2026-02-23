"""
STEP-10.3-2 — Emit a single LIVE CANARY signal (NO EXECUTION)

This script:
- Emits ONE live signal
- Requires LIVE_CANARY mode
- Does NOT execute trades
- Moves system to PENDING_LIVE_APPROVAL
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
from datetime import datetime
from uuid import uuid4

# ------------------------------------------------------------
# SAFETY: ENV CHECKS
# ------------------------------------------------------------

TRADING_ENV = os.getenv("TRADING_ENV", "").lower()
EXECUTION_ENABLED = os.getenv("EXECUTION_ENABLED", "false").lower() == "true"
REQUIRE_HUMAN_APPROVAL = os.getenv("REQUIRE_HUMAN_APPROVAL", "false").lower() == "true"

if TRADING_ENV != "live_canary":
    raise RuntimeError("emit_live_signal can only be run in LIVE_CANARY mode")

if not REQUIRE_HUMAN_APPROVAL:
    raise RuntimeError("Human approval must be enabled for live canary")

# ------------------------------------------------------------
# CANARY SIGNAL DEFINITION (LOCKED)
# ------------------------------------------------------------

STRATEGY_ID = "STRAT_CANARY"
SYMBOL = "RELIANCE"
SIDE = "BUY"
CONFIDENCE = 0.90
QTY = 1

order_id = f"CANARY_{uuid4().hex[:8]}"
timestamp = datetime.utcnow().isoformat()

# ------------------------------------------------------------
# EMIT SIGNAL (NO EXECUTION)
# ------------------------------------------------------------

signal = {
    "order_id": order_id,
    "strategy_id": STRATEGY_ID,
    "symbol": SYMBOL,
    "side": SIDE,
    "qty": QTY,
    "confidence": CONFIDENCE,
    "timestamp": timestamp,
    "mode": "LIVE_CANARY",
    "state": "PENDING_LIVE_APPROVAL",
}

# ------------------------------------------------------------
# OUTPUT (THIS IS THE CONTRACT)
# ------------------------------------------------------------

print("\n🟡 LIVE CANARY SIGNAL EMITTED")
print(f"order_id: {order_id}")
print(f"strategy: {STRATEGY_ID}")
print(f"symbol: {SYMBOL}")
print(f"side: {SIDE}")
print(f"qty: {QTY}")
print(f"confidence: {CONFIDENCE}")
print("state: PENDING_LIVE_APPROVAL")

# ------------------------------------------------------------
# NOTE:
# No broker calls
# No execution
# No retries
# ------------------------------------------------------------
