from typing import Dict, Any


def replay_risk(snapshot) -> Dict[str, Any]:
    """
    Replay recorded risk decisions.
    """
    risk_state = snapshot.components.get("risk_state", {})
    return {
        "blocks": risk_state.get("blocks", []),
        "warnings": risk_state.get("warnings", []),
        "raw": risk_state,
    }