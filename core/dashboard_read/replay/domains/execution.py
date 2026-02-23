from typing import Dict, Any


def replay_execution(snapshot) -> Dict[str, Any]:
    """
    Replay recorded execution intent.
    """
    execution = snapshot.components.get("execution_state", {})
    return {
        "orders": execution.get("orders", []),
        "count": len(execution.get("orders", [])),
        "raw": execution,
    }