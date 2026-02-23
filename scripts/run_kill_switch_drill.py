# scripts/run_kill_switch_drill.py

from core.execution.execute import execute_signal
from core.execution.execution_mode import ExecutionMode
from core.execution.governance import (
    ExecutionGovernance,
    ExecutionPromotion,
)
from core.operations.arming import (
    ExecutionArming,
    SystemArmingState,
)


signal = {
    "symbol": "INFY",
    "side": "BUY",
    "quantity": 1,
    "strategy_id": "KILL_SWITCH_DRILL",
}


print("\n=== KILL SWITCH DRILL START ===\n")

print("1) ARM system and execute PAPER (should succeed)")
result = execute_signal(
    signal=signal,
    mode=ExecutionMode.PAPER,
    governance=ExecutionGovernance(
        promotion_level=ExecutionPromotion.SHADOW_AND_PAPER
    ),
    arming=ExecutionArming(
        state=SystemArmingState.ARMED
    ),
)
print("✔ Success:", result.execution_id)

print("\n2) DISARM system and execute PAPER (should FAIL)")
try:
    execute_signal(
        signal=signal,
        mode=ExecutionMode.PAPER,
        governance=ExecutionGovernance(
            promotion_level=ExecutionPromotion.SHADOW_AND_PAPER
        ),
        arming=ExecutionArming(
            state=SystemArmingState.DISARMED
        ),
    )
    raise RuntimeError("❌ Kill switch FAILED")
except Exception as exc:
    print("✔ Kill switch engaged:", exc)

print("\n=== KILL SWITCH DRILL COMPLETE ===\n")
