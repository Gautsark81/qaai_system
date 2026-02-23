from typing import Dict, Any


def replay_strategy(snapshot) -> Dict[str, Any]:
    """
    Replay recorded strategy lifecycle state.
    No computation. No inference.
    """
    strategies = snapshot.components.get("strategies", {})
    return {
        "count": len(strategies),
        "strategies": list(strategies.keys()),
        "raw": strategies,
    }