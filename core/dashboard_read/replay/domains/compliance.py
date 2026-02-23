from typing import Dict, Any


def replay_compliance(snapshot) -> Dict[str, Any]:
    """
    Replay compliance and incident markers.
    """
    incidents = snapshot.components.get("incidents", [])
    return {
        "incident_count": len(incidents),
        "incidents": incidents,
    }