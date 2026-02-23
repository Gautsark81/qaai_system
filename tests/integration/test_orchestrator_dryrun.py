# tests/integration/test_orchestrator_dryrun.py
import time
import pytest
import importlib

# Resolve simulator class adaptively:
SIM_CLASS = None
try:
    # some versions may expose a test simulator directly in infra.dhan_client
    from infra.dhan_client import DhanClientSim  # type: ignore
    SIM_CLASS = DhanClientSim
except Exception:
    try:
        # fallback to sandbox adapter in infra.dhan_adapter
        from infra.dhan_adapter import DhanAdapterSandbox  # type: ignore
        SIM_CLASS = DhanAdapterSandbox
    except Exception:
        SIM_CLASS = None

from infra.dhan_adapter import DhanAdapter  # adapter wrapper

# Import orchestrator + risk manager adaptively
orch_mod = importlib.import_module("execution.orchestrator")
rm_mod = importlib.import_module("execution.risk_manager")


def _make_orchestrator_with_client(client):
    Orchestrator = getattr(orch_mod, "Orchestrator", None)
    if Orchestrator is None:
        pytest.skip("execution.orchestrator.Orchestrator not present")

    try:
        return Orchestrator(client=client)
    except TypeError:
        try:
            return Orchestrator({"client": client})
        except Exception:
            inst = Orchestrator()
            setattr(inst, "client", client)
            return inst


def test_orchestrator_dryrun_submit_and_fill():
    if SIM_CLASS is None:
        pytest.skip("No simulator available in infra; skipping integration dryrun.")

    # instantiate simulator (be tolerant to constructor signature)
    try:
        sim = SIM_CLASS(default_latency_sec=0.0)
    except TypeError:
        try:
            sim = SIM_CLASS()
        except Exception:
            sim = SIM_CLASS(api_key="sandbox")

    adapter = DhanAdapter(client=sim)
    orch = _make_orchestrator_with_client(adapter)

    # ensure risk manager exists
    rm = getattr(orch, "risk_manager", None)
    if rm is None:
        rm = rm_mod.RiskManager({"starting_cash": 100000.0})
        setattr(orch, "risk_manager", rm)

    # submit an order via orchestrator if it exposes a method, else use adapter
    order_id = None
    for m in ("submit_order", "place_order", "execute_order"):
        fn = getattr(orch, m, None)
        if callable(fn):
            order_id = fn(symbol="NSE:SIM", qty=1, price=100.0, side="BUY")
            break

    if order_id is None:
        order_id = adapter.place_order("NSE:SIM", 1, 100.0, side="BUY")
        hook = getattr(orch, "on_order_placed", None)
        if callable(hook):
            hook({"order_id": order_id, "symbol": "NSE:SIM", "qty": 1, "price": 100.0, "status": "ack"})

    assert order_id is not None

    # simulate fill
    if hasattr(adapter.client, "simulate_fill"):
        adapter.client.simulate_fill(order_id, filled_qty=1, fill_price=100.0)
    elif hasattr(adapter.client, "simulate_trade"):
        adapter.client.simulate_trade(order_id, 1, 100.0)

    # give orchestrator some time if it processes fills asynchronously
    time.sleep(0.1)

    rm = getattr(orch, "risk_manager", rm)
    hist = getattr(rm, "trade_history", None)
    active = getattr(rm, "active_trades", None)
    assert (hist and isinstance(hist, list)) or (active and isinstance(active, dict))
