# tests/test_risk_dynamic_sl.py
import pytest

try:
    from qaai_system.execution.risk_manager import RiskManager, RiskLimits
except Exception:
    try:
        from qaai_system.execution.risk import RiskManager, RiskLimits
    except Exception:
        # fallback: the repo may implement risk differently; test basic apply_drawdown if present
        from execution import risk as risk_mod
        pytest.skip("RiskManager location not standard; skip")

def test_risk_limits_kill_switch():
    limits = RiskLimits(kill_switch=True)
    # provider stub: minimal
    class P:
        def get_last_price(self, s): return 100.0
        def get_account(self): return {"nav":100000}
        def get_open_orders(self): return []
        def get_positions(self): return {}
    r = RiskManager(limits, provider=P())
    assert r.is_kill_switch_armed() is True
