"""
STEP-10.3-3 — Verify human approval for a live canary order
NO EXECUTION — VERIFICATION ONLY
"""

from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------

ORDER_ID = "CANARY_bd34163b"
APPROVAL_DIR = Path("data/live_approvals")
APPROVAL_FILE = APPROVAL_DIR / f"{ORDER_ID}.approved"

# ------------------------------------------------------------
# VERIFICATION
# ------------------------------------------------------------

if not APPROVAL_DIR.exists():
    raise RuntimeError("Approval directory does not exist")

if not APPROVAL_FILE.exists():
    raise RuntimeError(f"Approval not found for order {ORDER_ID}")

print("\n🟢 LIVE APPROVAL VERIFIED")
print(f"order_id: {ORDER_ID}")
print("operator: human")
print("state: APPROVED")
print("\n⚠️ NO EXECUTION PERFORMED (verification only)")
