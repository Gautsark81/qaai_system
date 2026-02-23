from core.execution.execute import execute_signal
from core.execution.execution_mode import ExecutionMode

signal = {
    "symbol": "INFY",
    "side": "BUY",
    "quantity": 10,
    "strategy_id": "STRAT_TEST_001",
}

result = execute_signal(
    signal=signal,
    mode=ExecutionMode.SHADOW,
    emit_telemetry=True,
)

print(result)
