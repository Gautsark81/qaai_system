# tests/integration/test_dryrun_smoke.py
import pytest
from infra.dhan_client_sim import DhanClientSim

def test_simulator_place_and_fill():
    sim = DhanClientSim(seed=123, default_latency_sec=0.0)
    oid = sim.place_order("NSE:TEST", 10, 100.0, "BUY")
    assert oid.startswith("sim-")
    ev = sim.simulate_fill(oid, filled_qty=5, fill_price=100.0)
    assert ev["filled_qty"] == 5
    s = sim.get_order(oid)
    assert s.filled_qty == 5
    # finish fill
    sim.simulate_fill(oid, filled_qty=5, fill_price=100.0)
    s2 = sim.get_order(oid)
    assert s2.status == "FILLED"
    assert s2.filled_qty == 10

@pytest.mark.skipif(True, reason="Template integration test — enable and adapt to your orchestrator")
def test_integration_orchestrator_dryrun():
    """
    TEMPLATE: adapt this test to your orchestrator entrypoint.

    Example:
      from main_orchestrator import MainOrchestrator
      orchestrator = MainOrchestrator(dry_run=True, client=sim)
      orchestrator.start_once_for_test(...)
    """
    import importlib
    try:
        mo = importlib.import_module("main_orchestrator")
    except Exception:
        pytest.skip("main_orchestrator not available in test environment")

    # If your main_orchestrator exposes a 'run' or 'start' method, call it here in dry-run mode:
    if hasattr(mo, "run"):
        sim = DhanClientSim(seed=1)
        # environment / configuration: ensure the orchestrator uses the injected client
        # This is a template — adapt to your codebase.
        mo.run(dry_run=True, client=sim)
    else:
        pytest.skip("no supported orchestrator entrypoint found")
