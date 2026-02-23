"""
Operator Dashboard Bootstrap
============================

Purpose
-------
This file establishes a SINGLE, CANONICAL import root for the entire
Operator Dashboard system.

It guarantees:
• `intelligence/` is importable
• `modules/operator_dashboard/` resolves cleanly
• Streamlit hot-reload does NOT break imports
• No page ever touches sys.path again

This file MUST be imported first in:
• dashboard_app.py
• every Streamlit page (pages/*.py)

Doctrine
--------
Stability first → Adaptivity second → Intelligence last
"""

from __future__ import annotations

import sys
from pathlib import Path


# ------------------------------------------------------------
# 1️⃣ Resolve Repository Root (deterministic & portable)
# ------------------------------------------------------------

# This file lives at:
# <repo_root>/modules/operator_dashboard/bootstrap.py
REPO_ROOT = Path(__file__).resolve().parents[2]

if not REPO_ROOT.exists():
    raise RuntimeError(f"Repo root not found: {REPO_ROOT}")


# ------------------------------------------------------------
# 2️⃣ Inject Repo Root into sys.path (idempotent)
# ------------------------------------------------------------

repo_root_str = str(REPO_ROOT)

if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)


# ------------------------------------------------------------
# 3️⃣ Optional Safety Assertions (fail fast, fail loud)
# ------------------------------------------------------------

REQUIRED_DIRS = [
    REPO_ROOT / "intelligence",
    REPO_ROOT / "modules" / "operator_dashboard",
]

for d in REQUIRED_DIRS:
    if not d.exists():
        raise RuntimeError(
            f"Critical directory missing: {d}\n"
            "Dashboard cannot start without this."
        )


# ------------------------------------------------------------
# 4️⃣ Diagnostic Helper (optional, safe)
# ------------------------------------------------------------

def debug_bootstrap() -> dict:
    """Return bootstrap diagnostics for debugging/UI display."""
    return {
        "repo_root": str(REPO_ROOT),
        "sys_path_head": sys.path[:3],
        "intelligence_exists": (REPO_ROOT / "intelligence").exists(),
        "operator_dashboard_exists": (
            REPO_ROOT / "modules" / "operator_dashboard"
        ).exists(),
    }
