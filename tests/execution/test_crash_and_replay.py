import tempfile

from qaai_system.execution.execution_engine import ExecutionEngine
from qaai_system.execution.order_manager import OrderManager

from core.capital.capital_allocator import CapitalDecision


# ============================================================
# BASIC REPLAY SAFETY
# ============================================================

def test_execution_replay_is_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        journal_path = f"{tmp}/exec.journal"

        # ---- First run ----
        engine1 = ExecutionEngine(
            config={"execution_journal_path": journal_path},
        )

        resp = engine1.submit(
            {"symbol": "NIFTY", "side": "BUY", "quantity": 1, "price": 100}
        )

        order_id = resp["order_id"]
        engine1.monitor_open_orders()

        orders_run1 = engine1.order_manager.get_all_orders()
        assert len(orders_run1) == 1

        # ---- Simulate crash ----
        del engine1

        # ---- Restart ----
        engine2 = ExecutionEngine(
            config={"execution_journal_path": journal_path},
        )

        drifts = engine2.reconcile_on_startup()
        assert drifts == []

        orders_run2 = engine2.order_manager.get_all_orders()
        assert len(orders_run2) == 1
        assert order_id in orders_run2


def test_fill_not_duplicated_on_replay():
    with tempfile.TemporaryDirectory() as tmp:
        journal_path = f"{tmp}/exec.journal"

        engine = ExecutionEngine(
            config={"execution_journal_path": journal_path},
        )

        engine.submit(
            {"symbol": "NIFTY", "side": "BUY", "quantity": 1, "price": 100}
        )

        engine.monitor_open_orders()
        fills_before = len(engine._seen_fills)
        assert fills_before == 1

        # Restart
        engine_replay = ExecutionEngine(
            config={"execution_journal_path": journal_path},
        )
        engine_replay.reconcile_on_startup()

        fills_after = len(engine_replay._seen_fills)
        assert fills_after == 1


# ============================================================
# CAPITAL GOVERNANCE — TEST-SAFE STUB
# ============================================================

class DummyCapitalEngine:
    """
    Pure stub.
    Intentionally does NOT inherit from CapitalDecisionEngine.
    """

    def decide(self, **kwargs):
        return CapitalDecision(
            decision=CapitalDecision.ALLOW,
            multiplier=1.0,
            reasons=["test"],
        )


def test_capital_not_double_applied_after_restart():
    with tempfile.TemporaryDirectory() as tmp:
        journal_path = f"{tmp}/exec.journal"

        engine = ExecutionEngine(
            capital_engine=DummyCapitalEngine(),
            config={"execution_journal_path": journal_path},
        )

        # 🔒 Deterministic intent creation
        engine.submit(
            {"symbol": "NIFTY", "side": "BUY", "quantity": 1, "price": 100}
        )

        orders_before = len(engine.order_manager.get_all_orders())
        assert orders_before == 1

        # ---- Restart ----
        engine2 = ExecutionEngine(
            capital_engine=DummyCapitalEngine(),
            config={"execution_journal_path": journal_path},
        )
        engine2.reconcile_on_startup()

        orders_after = len(engine2.order_manager.get_all_orders())
        assert orders_after == 1



# ============================================================
# CRASH SAFETY
# ============================================================

def test_crash_between_intent_and_fill_is_safe():
    with tempfile.TemporaryDirectory() as tmp:
        journal_path = f"{tmp}/exec.journal"

        engine = ExecutionEngine(
            config={"execution_journal_path": journal_path},
        )

        resp = engine.submit(
            {"symbol": "NIFTY", "side": "BUY", "quantity": 1, "price": 100}
        )
        order_id = resp["order_id"]

        # Crash BEFORE monitor_open_orders()
        del engine

        # Restart
        engine2 = ExecutionEngine(
            config={"execution_journal_path": journal_path},
        )
        engine2.reconcile_on_startup()

        orders = engine2.order_manager.get_all_orders()
        assert order_id in orders
        assert orders[order_id]["status"] in {"open", "new"}


def test_no_phantom_pnl_on_replay():
    with tempfile.TemporaryDirectory() as tmp:
        journal_path = f"{tmp}/exec.journal"

        trade_log = type("TL", (), {"logged_trades": []})()

        engine = ExecutionEngine(
            trade_logger=trade_log,
            config={"execution_journal_path": journal_path},
        )

        engine.submit(
            {"symbol": "NIFTY", "side": "BUY", "quantity": 1, "price": 100}
        )
        engine.monitor_open_orders()

        pnl_before = sum(t["pnl"] for t in trade_log.logged_trades)

        engine2 = ExecutionEngine(
            trade_logger=trade_log,
            config={"execution_journal_path": journal_path},
        )
        engine2.reconcile_on_startup()

        pnl_after = sum(t["pnl"] for t in trade_log.logged_trades)
        assert pnl_before == pnl_after
