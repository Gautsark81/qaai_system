"""
Execution test namespace bootstrap.

Tests intentionally do not import execution primitives.
This file provides the stable public execution API.
"""

import os
import sys
import pathlib
import asyncio
import pytest
import builtins

# =============================================================================
# CRITICAL: freeze environment BEFORE anything else
# =============================================================================
os.environ["MOCK_DB"] = "1"
os.environ["MODE"] = "paper"
os.environ["ACCOUNT_EQUITY"] = "1000000"

# =============================================================================
# Ensure project root is first in sys.path
# =============================================================================
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
PROJECT_ROOT_STR = str(PROJECT_ROOT)

# Remove duplicates
sys.path = [p for p in sys.path if p != PROJECT_ROOT_STR]

# Insert at position 0
sys.path.insert(0, PROJECT_ROOT_STR)

# =============================================================================
# Diagnostics (safe)
# =============================================================================
def _show_import_location(pkg_name: str):
    try:
        m = __import__(pkg_name)
        print(
            f"conftest: {pkg_name} -> {getattr(m, '__file__', repr(m))}",
            file=sys.stderr,
        )
    except Exception:
        print(
            f"conftest: {pkg_name} not importable",
            file=sys.stderr,
        )

_show_import_location("clients")
_show_import_location("config")
_show_import_location("features")
_show_import_location("providers")
_show_import_location("backtester")
_show_import_location("tests")

# =============================================================================
# Asyncio deterministic shutdown (Windows fix)
# =============================================================================
@pytest.fixture(scope="session", autouse=True)
def _force_asyncio_cleanup():
    yield
    try:
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
    except Exception:
        pass

# =============================================================================
# Inject execution primitives into builtins (required by execution tests)
# =============================================================================
from core.execution.engine import ExecutionEngine
from core.execution.idempotency_ledger.ledger import ExecutionIdempotencyLedger
from core.execution.execution_intent import ExecutionIntent

builtins.ExecutionEngine = ExecutionEngine
builtins.ExecutionIdempotencyLedger = ExecutionIdempotencyLedger
builtins.ExecutionIntent = ExecutionIntent