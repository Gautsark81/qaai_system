# tools/phase_map.py

PHASE_MAP = {
    # Execution phases
    "modules/core": "0",
    "modules/strategies": "1",
    "modules/features": "2",
    "modules/backtest": "3",
    "modules/risk": "4",
    "modules/execution": "5",
    "modules/strategy_lifecycle": "6",
    "modules/runtime": "7",
    "modules/invariants": "8",
    "modules/execution_gate": "9",
    "model_ops/capital": "10",
    "model_ops/capital_dynamics": "11",
    "model_ops/portfolio": "12",
    "model_ops/autonomy": "13",

    # Architectural phases
    "modules/pure": "A",
    "modules/state": "B",
    "modules/ssot": "C",
    "modules/time": "D",
    "modules/restart": "E",
    "modules/idempotency": "F",
    "modules/contracts": "G",
    "modules/no_flags": "H",
    "modules/determinism": "I",
    "modules/model_ops": "J",
    "modules/explainability": "K",
    "modules/governance": "L",
}
