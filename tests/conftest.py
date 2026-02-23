# tests/conftest.py

# =============================================================================
# CRITICAL: freeze environment BEFORE any project imports
# =============================================================================
import os

os.environ.setdefault("MOCK_DB", "1")
os.environ.setdefault("MODE", "paper")
os.environ.setdefault("ACCOUNT_EQUITY", "1000000")

# =============================================================================
# Standard imports AFTER env is frozen
# =============================================================================
import sys
import pathlib
import pytest
import importlib.util
import builtins
import asyncio
import gc
import warnings
from typing import Dict, Any, List

# =============================================================================
# EXECUTION PUBLIC NAMESPACE INJECTION (REQUIRED BY EXECUTION TESTS)
# =============================================================================
from core.execution.engine import ExecutionEngine
from core.execution.idempotency_ledger.ledger import ExecutionIdempotencyLedger
from core.execution.execution_intent import ExecutionIntent

builtins.ExecutionEngine = ExecutionEngine
builtins.ExecutionIdempotencyLedger = ExecutionIdempotencyLedger
builtins.ExecutionIntent = ExecutionIntent


# =============================================================================
# PATH SETUP (Deterministic and Safe)
# =============================================================================
TEST_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent


def _ensure_on_syspath_front(p: pathlib.Path):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)


def _ensure_on_syspath_append(p: pathlib.Path):
    s = str(p)
    if s not in sys.path:
        sys.path.append(s)


# Ensure project root first
_ensure_on_syspath_front(PROJECT_ROOT)

# Support src/ layout
src_dir = PROJECT_ROOT / "src"
if src_dir.exists():
    _ensure_on_syspath_append(src_dir)

# Add immediate children safely (no recursion)
for child in PROJECT_ROOT.iterdir():
    try:
        if not child.is_dir():
            continue
        if child == PROJECT_ROOT or child == src_dir:
            continue
        if (child / "__init__.py").exists():
            _ensure_on_syspath_append(child)
    except PermissionError:
        continue


# =============================================================================
# Diagnostics (Non-fatal)
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


# =============================================================================
# Ignore future roadmap test directories
# =============================================================================
def pytest_ignore_collect(collection_path, config):
    path_str = str(collection_path).replace("\\", "/")
    FUTURE_TEST_ROOTS = (
        "tests/domain",
        "tests/graduation",
    )
    return any(root in path_str for root in FUTURE_TEST_ROOTS)


# =============================================================================
# Optional Orchestrator Patch Loader
# =============================================================================
@pytest.fixture(scope="session", autouse=True)
def apply_orchestrator_patch():
    try:
        import qaai_system.patch_orchestrator  # noqa
    except Exception:
        patch_path = os.path.abspath("/mnt/data/patch_orchestrator.py")
        if os.path.exists(patch_path):
            spec = importlib.util.spec_from_file_location(
                "qaai_system.patch_orchestrator", patch_path
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules["qaai_system.patch_orchestrator"] = mod
            spec.loader.exec_module(mod)
    yield


# =============================================================================
# GLOBAL ASYNCIO STRICT CLEANUP (Windows Proactor safe)
# =============================================================================
@pytest.fixture(scope="session", autouse=True)
def _strict_asyncio_cleanup():
    """
    Production-grade asyncio cleanup for pytest STRICT mode on Windows.

    Prevents:
    - Unclosed socket warnings
    - ProactorEventLoop leaks
    - Pending task leaks
    - Executor thread leaks
    - Async generator leaks
    - pytest unraisable escalation
    """

    yield

    try:
        policy = asyncio.get_event_loop_policy()
        loop = policy.get_event_loop()
    except RuntimeError:
        return

    if loop.is_closed():
        return

    try:
        # -------------------------------------------------
        # Cancel all pending tasks
        # -------------------------------------------------
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()

        if pending:
            loop.run_until_complete(
                asyncio.gather(*pending, return_exceptions=True)
            )

        # -------------------------------------------------
        # Shutdown async generators
        # -------------------------------------------------
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass

        # -------------------------------------------------
        # Shutdown default executor (VERY important)
        # -------------------------------------------------
        try:
            loop.run_until_complete(loop.shutdown_default_executor())
        except Exception:
            pass

        # -------------------------------------------------
        # Close loop
        # -------------------------------------------------
        loop.close()

    except Exception:
        pass

    # -------------------------------------------------
    # Reset event loop policy (critical on Windows)
    # -------------------------------------------------
    try:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    except Exception:
        pass

    # -------------------------------------------------
    # Suppress benign Windows socket ResourceWarnings
    # -------------------------------------------------
    warnings.filterwarnings("ignore", category=ResourceWarning)

    # -------------------------------------------------
    # Final garbage collection
    # -------------------------------------------------
    gc.collect()


# =============================================================================
# Dummy Provider
# =============================================================================
class DummyProvider:
    def __init__(self):
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.counter = 0

    def submit_order(self, order: Dict[str, Any]) -> str:
        self.counter += 1
        oid = f"dummy_{self.counter}"
        self.orders[oid] = dict(order)
        return oid

    def fetch_fills_for_order_ids(self, order_ids: List[str]):
        fills = []
        for oid in order_ids:
            order = self.orders.get(oid, {})
            fills.append(
                {
                    "order_id": oid,
                    "qty": int(order.get("quantity", 0)),
                    "price": float(order.get("price", 150)),
                    "side": order.get("side", "buy"),
                }
            )
        return fills


# =============================================================================
# Helpers
# =============================================================================
class DummyStrategy:
    def __init__(self, sid: str, orders: List[Dict[str, Any]]):
        self.id = sid
        self._orders = orders

    def generate_orders(self, market_data):
        return list(self._orders)


def make_order(symbol="AAA", side="buy", qty=100, price=10.0):
    return {
        "symbol": symbol,
        "side": side,
        "quantity": qty,
        "price": price,
    }
