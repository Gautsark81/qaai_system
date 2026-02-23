import threading
import random
import pytest
from qaai_system.execution.execution_engine import ExecutionEngine


# --------------------
# Dummy helpers for testing
# --------------------
class DummyTradeLogger:
    def __init__(self):
        self.logged_trades = []

    def log_trade(self, trade_event):
        """Simulate trade logging without touching production DB/files."""
        self.logged_trades.append(trade_event)


class DummySignalEngine:
    def __init__(self):
        self.config = {
            "sl_tp": {"stop_loss_pct": 0.01, "take_profit_pct": 0.02},
            "base_position_size": 100,
        }
        self.trade_history = {}

    def register_trade_result(
        self, trade_id, pnl, sl_hit=False, tp_hit=False, meta=None
    ):
        reason = []
        if sl_hit:
            reason.append("Stop Loss Hit")
        if tp_hit:
            reason.append("Take Profit Hit")
        if meta:
            reason.append(
                f"ML Score={meta.get('ml_score')}, Rule Score={meta.get('rule_score')}"
            )
        self.trade_history[trade_id] = {"pnl": pnl, "reason": " | ".join(reason)}


# --------------------
# Fixtures
# --------------------
@pytest.fixture
def exec_engine(monkeypatch):
    """ExecutionEngine wired with dummy managers and signal engine for testing."""
    # Create dummy dependencies
    dummy_order_manager = type(
        "DummyOrderManager",
        (),
        {
            "create_order": lambda *a, **k: "order1",
            "get_all_orders": lambda *a, **k: {
                "order1": {
                    "status": "closed",
                    "entry_price": 100,
                    "side": "buy",
                    "quantity": 1,
                }
            },
            "update_order_status": lambda *a, **k: None,
            "open_orders": {},
        },
    )()
    dummy_risk_manager = object()
    dummy_trade_logger = DummyTradeLogger()

    # Minimal config
    config = {
        "fill_poll_interval": 1,
        "sl_tp": {"enabled": True, "stop_loss_pct": 0.02, "take_profit_pct": 0.03},
    }

    # Instantiate with real signature
    engine = ExecutionEngine(
        signal_provider=None,
        order_manager=dummy_order_manager,
        risk_manager=dummy_risk_manager,
        trade_logger=dummy_trade_logger,
        broker_adapter=None,
        config=config,
    )

    # Inject dummy signal engine
    engine.signal_engine = DummySignalEngine()
    return engine


# --------------------
# Existing core tests
# --------------------
def test_tp_hit_updates_feedback(exec_engine):
    fill_event = {
        "trade_id": "T1",
        "symbol": "RELIANCE",
        "filled_qty": 1,
        "avg_fill_price": 100,
        "side": "BUY",
        "status": "CLOSED",
        "close_reason": "TP",
        "pnl": 50.0,
    }
    exec_engine.on_fill(fill_event)
    assert exec_engine.trade_logger.logged_trades[-1]["close_reason"] == "TP"


def test_sl_hit_updates_feedback(exec_engine):
    fill_event = {
        "trade_id": "T2",
        "symbol": "RELIANCE",
        "filled_qty": 1,
        "avg_fill_price": 100,
        "side": "BUY",
        "status": "CLOSED",
        "close_reason": "SL",
        "pnl": -20.0,
    }
    exec_engine.on_fill(fill_event)
    assert exec_engine.trade_logger.logged_trades[-1]["close_reason"] == "SL"


def test_auto_tune_on_batch(exec_engine):
    for i in range(3):
        exec_engine.on_fill(
            {
                "trade_id": f"L{i}",
                "symbol": "RELIANCE",
                "filled_qty": 1,
                "avg_fill_price": 100,
                "side": "BUY",
                "status": "CLOSED",
                "close_reason": "SL",
                "pnl": -10.0,
            }
        )
    assert len(exec_engine.trade_logger.logged_trades) >= 3


def test_concurrency_stress(exec_engine):
    def worker():
        exec_engine.on_fill(
            {
                "trade_id": threading.current_thread().name,
                "symbol": "RELIANCE",
                "filled_qty": 1,
                "avg_fill_price": 100,
                "side": "BUY",
                "status": "CLOSED",
                "close_reason": "TP",
                "pnl": 5.0,
            }
        )

    threads = [threading.Thread(target=worker, name=f"thr-{i}") for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(exec_engine.trade_logger.logged_trades) >= 20


# --------------------
# New enhancement tests
# --------------------
def test_volatility_and_regime_sl_tp_scaling(exec_engine):
    """Ensure SL/TP adjust based on ATR and regime."""
    initial_sl = exec_engine.signal_engine.config["sl_tp"]["stop_loss_pct"]
    atr = 0.015
    regime_factor = 1.5
    exec_engine.signal_engine.config["sl_tp"]["stop_loss_pct"] = atr * regime_factor
    assert exec_engine.signal_engine.config["sl_tp"]["stop_loss_pct"] != initial_sl
    assert exec_engine.signal_engine.config["sl_tp"]["stop_loss_pct"] == pytest.approx(
        0.0225
    )


def test_position_size_auto_tuning_under_drawdown(exec_engine):
    """Ensure position size shrinks after losing streak."""
    initial_size = exec_engine.signal_engine.config["base_position_size"]
    for _ in range(5):
        exec_engine.signal_engine.register_trade_result("X", -10, sl_hit=True)
        exec_engine.signal_engine.config["base_position_size"] *= 0.9
    assert exec_engine.signal_engine.config["base_position_size"] < initial_size


def test_trade_reason_logging(exec_engine):
    """Ensure a descriptive reason string is logged."""
    trade_id = "R1"
    pnl = 20.0
    exec_engine.signal_engine.register_trade_result(
        trade_id,
        pnl,
        sl_hit=False,
        tp_hit=True,
        meta={
            "symbol": "RELIANCE",
            "side": "BUY",
            "ml_score": 0.82,
            "rule_score": 0.65,
        },
    )
    reason = exec_engine.signal_engine.trade_history[trade_id]["reason"]
    assert "Take Profit Hit" in reason
    assert "ML Score=0.82" in reason


# --------------------
# Battle Mode Stress Test
# --------------------
def test_battle_mode_high_volatility(exec_engine):
    """
    Simulate extreme market churn with mixed SL/TP hits and volatility scaling.
    Ensures feedback loop remains stable under stress.
    """
    max_threads = 50
    initial_size = exec_engine.signal_engine.config["base_position_size"]

    def worker(i):
        # Random volatility regime
        atr = random.uniform(0.005, 0.03)  # 0.5%–3% ATR
        regime_factor = random.uniform(0.8, 2.0)
        exec_engine.signal_engine.config["sl_tp"]["stop_loss_pct"] = atr * regime_factor
        exec_engine.signal_engine.config["sl_tp"]["take_profit_pct"] = (
            atr * regime_factor * 1.5
        )

        # Random trade outcome
        tp_hit = random.choice([True, False])
        sl_hit = not tp_hit
        pnl = random.uniform(-50, 50)

        exec_engine.on_fill(
            {
                "trade_id": f"BATTLE-{i}",
                "symbol": "RELIANCE",
                "filled_qty": 1,
                "avg_fill_price": 100,
                "side": "BUY",
                "status": "CLOSED",
                "close_reason": "TP" if tp_hit else "SL",
                "pnl": pnl,
            }
        )

        # Auto-tune position size on loss
        if pnl < 0:
            exec_engine.signal_engine.config["base_position_size"] *= 0.95

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(max_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Assertions after chaos
    final_sl = exec_engine.signal_engine.config["sl_tp"]["stop_loss_pct"]
    final_tp = exec_engine.signal_engine.config["sl_tp"]["take_profit_pct"]
    final_size = exec_engine.signal_engine.config["base_position_size"]

    assert 0.002 <= final_sl <= 0.06, f"SL% out of bounds: {final_sl}"
    assert 0.003 <= final_tp <= 0.09, f"TP% out of bounds: {final_tp}"
    assert final_size > 0, "Position size collapsed to zero"
    assert len(exec_engine.trade_logger.logged_trades) >= max_threads
