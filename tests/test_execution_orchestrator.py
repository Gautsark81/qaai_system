# tests/test_execution_orchestrator.py
import pytest
from unittest.mock import patch, MagicMock
from qaai_system.execution.orchestrator import ExecutionOrchestrator
import yaml


# Helper function to create a mock config for testing
def _make_config(tmp_path, mode="paper"):
    cfg = {
        "execution_mode": mode,
        "starting_cash": 1000000.0,
        "risk": {
            "kill_switch": False,
            "max_symbol_weight": 0.2,  # 20% of equity per symbol
        },
        "positions": {"method": "fifo"},
    }
    config_path = tmp_path / f"{mode}_config.yaml"
    config_path.write_text(yaml.safe_dump(cfg))
    return config_path


# Test: Order Submission and Status Update
def test_order_submission_and_status(tmp_path):
    cfg_path = _make_config(tmp_path, "paper")
    orch = ExecutionOrchestrator(config_path=cfg_path)

    order = {"symbol": "AAPL", "qty": 10, "side": "buy", "price": 100.0}

    with patch.object(orch.risk, "check_symbol_cap", return_value=True):
        order_id = orch.submit_order(order)

    assert order_id is not None
    status = orch.get_order_status(order_id)
    print(f"Order Status: {status}")

    assert "symbol" in status
    assert status["symbol"] == "AAPL"
    assert status["status"] in ("SUBMITTED", "FILLED")


def test_cancel_order(tmp_path):
    cfg_path = _make_config(tmp_path, "paper")
    orch = ExecutionOrchestrator(config_path=cfg_path)

    order = {"symbol": "TSLA", "qty": 5, "side": "sell", "price": 250.0}

    with patch.object(orch.risk, "check_symbol_cap", return_value=True):
        order_id = orch.submit_order(order)

    assert order_id is not None
    orch.cancel_order(order_id)
    status = orch.get_order_status(order_id)
    print(f"Cancelled Order Status: {status}")

    assert status["status"].lower() == "cancelled"


def test_symbol_cap_blocked(tmp_path):
    cfg_path = _make_config(tmp_path, "paper")
    orch = ExecutionOrchestrator(config_path=cfg_path)

    order = {"symbol": "AAPL", "qty": 1000, "side": "buy", "price": 100.0}

    with patch.object(orch.risk, "check_symbol_cap", return_value=False):
        with pytest.raises(ValueError, match="Symbol cap exceeded for AAPL"):
            orch.submit_order(order)


def test_risk_evaluation_blocked(tmp_path):
    cfg_path = _make_config(tmp_path, "paper")
    orch = ExecutionOrchestrator(config_path=cfg_path)

    order = {"symbol": "GOOG", "qty": 10, "side": "buy", "price": 1500.0}

    with patch.object(
        orch.risk,
        "evaluate_risk",
        return_value=(False, "Risk blocked: Order size too large"),
    ):
        with pytest.raises(
            ValueError, match="RISK_BLOCK: Risk blocked: Order size too large"
        ):
            orch.submit_order(order)


def test_account_status_check(tmp_path):
    cfg_path = _make_config(tmp_path, "paper")
    orch = ExecutionOrchestrator(config_path=cfg_path)

    with patch.object(orch.risk, "is_trading_allowed", return_value=False):
        order = {"symbol": "AAPL", "qty": 10, "side": "buy", "price": 100.0}
        with pytest.raises(ValueError, match="Trading not allowed by circuit breaker"):
            orch.submit_order(order)


def test_kill_switch_blocks_trading(tmp_path):
    cfg_path = _make_config(tmp_path)
    orch = ExecutionOrchestrator(config_path=cfg_path)

    orch.risk.set_kill_switch(True)
    order = {"symbol": "NFLX", "qty": 2, "side": "buy", "price": 400.0}

    orch.config["risk"] = {"kill_switch": True}
    with pytest.raises(RuntimeError, match="KILL_SWITCH_ACTIVE"):
        orch.submit_order(order)


def test_poll_feedback_dispatch(tmp_path):
    cfg_path = _make_config(tmp_path)
    mock_feedback = MagicMock()
    orch = ExecutionOrchestrator(config_path=cfg_path)
    orch._feedback_target = mock_feedback

    orch.provider.get_filled_orders = MagicMock(
        return_value=[
            {
                "order_id": "1",
                "symbol": "MSFT",
                "qty": 5,
                "side": "buy",
                "price": 300.0,
                "pnl": 50.0,
            }
        ]
    )

    orch.poll()

    assert mock_feedback.on_trade.called or mock_feedback.on_trade_closed.called


def test_order_status_merging(tmp_path):
    cfg_path = _make_config(tmp_path)
    orch = ExecutionOrchestrator(config_path=cfg_path)

    order = {"symbol": "AMZN", "qty": 3, "side": "buy", "price": 2000.0}
    with patch.object(orch.risk, "check_symbol_cap", return_value=True):
        order_id = orch.submit_order(order)

    orch.provider.get_order_status = MagicMock(
        return_value={
            "order_id": order_id,
            "status": "filled",
            "symbol": "AMZN",
            "filled_qty": 3,
        }
    )

    status = orch.get_order_status(order_id)
    assert status["status"].lower() == "filled"
    assert status["symbol"] == "AMZN"
    assert status["filled_qty"] == 3
