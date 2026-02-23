# tools/phase_resolver.py

EXECUTION_PHASES = {
    "core": "0",
    "strategies": "1",
    "features": "2",
    "backtest": "3",
    "risk": "4",
    "execution": "5",
    "strategy_lifecycle": "6",
    "runtime": "7",
    "invariants": "8",
    "execution_gate": "9",
    "capital": "10",
    "capital_dynamics": "11",
    "portfolio": "12",
    "autonomy": "13",
}

ARCH_PHASES = {
    "pure": "A",
    "state": "B",
    "ssot": "C",
    "time": "D",
    "restart": "E",
    "idempotency": "F",
    "contracts": "G",
    "no_flags": "H",
    "determinism": "I",
    "model_ops": "J",
    "explainability": "K",
    "governance": "L",
    "autonomy_bounds": "M",
}
