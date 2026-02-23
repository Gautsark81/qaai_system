from typing import Dict, Any


def replay_capital(snapshot) -> Dict[str, Any]:
    """
    Replay recorded capital state.
    """
    capital = snapshot.components.get("capital_state", {})
    return {
        "available": capital.get("available"),
        "used": capital.get("used"),
        "raw": capital,
    }