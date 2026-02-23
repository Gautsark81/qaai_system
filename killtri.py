from core.safety.kill_switch import KillSwitch
from core.safety.scopes import KillScope
from core.paper.paper_executor import PaperExecutor

ks = KillSwitch()
executor = PaperExecutor(kill_switch=ks)

# Kill only STRAT_A
ks.trip(KillScope.STRATEGY, key="STRAT_A", reason="anomaly_detected")

# ❌ Should FAIL
executor.execute(
    strategy_id="STRAT_A",
    symbol="RELIANCE",
    side="BUY",
    qty=10,
    price=2500,
)

# ✅ Should PASS
executor.execute(
    strategy_id="STRAT_B",
    symbol="RELIANCE",
    side="BUY",
    qty=5,
    price=2500,
)
