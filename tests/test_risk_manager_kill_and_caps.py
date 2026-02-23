# tests/test_risk_manager_kill_and_caps.py
import yaml
import pytest
from qaai_system.execution.orchestrator import ExecutionOrchestrator


def _write_config(tmp_path, risk_cfg):
    cfg = {"execution_mode": "paper", "risk": risk_cfg}
    p = tmp_path / "execution.yaml"
    with open(p, "w") as f:
        yaml.safe_dump(cfg, f)
    return str(p)


def test_kill_switch_blocks_orders(tmp_path):
    # config with kill switch armed
    cfg_path = _write_config(tmp_path, {"kill_switch": True})
    orch = ExecutionOrchestrator(config_path=cfg_path)
    order = {"symbol": "KILL", "qty": 10, "side": "buy", "price": 100.0}
    with pytest.raises(RuntimeError) as exc:
        orch.submit_order(order)
    assert "KILL_SWITCH_ACTIVE" in str(exc.value)


def test_symbol_cap_blocks_order(tmp_path):
    # small nav and tight symbol cap to force symbol cap block
    risk_cfg = {
        "kill_switch": False,
        "max_gross_exposure": 1.0,
        "max_symbol_weight": 0.5,  # 50% of NAV
        "max_order_notional": 1e6,
        "max_open_orders": 10,
    }
    cfg_path = _write_config(tmp_path, risk_cfg)
    orch = ExecutionOrchestrator(config_path=cfg_path)
    provider = orch.provider
    # set NAV low so symbol cap kicks in quickly
    provider._account_nav = 10000.0  # NAV
    # set last price for symbol
    provider._positions["__last_price__:SYM"] = 100.0
    # current position = 45 -> notional = 4500
    provider._positions["SYM"] = 45

    # placing buy of 10 @ 100 -> future notional = 5500 > cap (0.5 * 10000 = 5000)
    order = {"symbol": "SYM", "qty": 10, "side": "buy", "price": 100.0}
    with pytest.raises(ValueError) as exc:
        orch.submit_order(order)
    assert "RISK_BLOCK: symbol_cap" in str(exc.value)


def test_kill_switch_cancel_open_orders(tmp_path):
    # config where kill_switch can be armed via method
    cfg_path = _write_config(tmp_path, {"kill_switch": False})
    orch = ExecutionOrchestrator(config_path=cfg_path)
    provider = orch.provider

    # create a mock open order in provider internals
    oid = provider._next_id()
    provider._orders[oid] = {
        "order_id": oid,
        "symbol": "ZZ",
        "qty": 10,
        "status": "NEW",
        "filled_qty": 0,
        "avg_price": 0.0,
    }

    # arm kill switch via orchestrator and cancel open orders
    canceled = orch.arm_kill_switch()
    assert canceled >= 1
    # order should be canceled
    st = provider.get_order_status(oid)
    assert st["status"] == "CANCELLED"
