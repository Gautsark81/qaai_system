# File: core/dashboard/export.py
#
# Stable dashboard export contract.
# Used by UI, operators, and future intelligence layers.
# READ-ONLY. NO AUTHORITY.

from datetime import datetime
from core.dashboard.roadmap import get_full_roadmap


def export_dashboard_state() -> dict:
    """
    Exports the canonical dashboard snapshot.
    """

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system_health": {
            "armed": False,
            "capital_governed": True,
            "execution_allowed": False,
        },
        "roadmap": get_full_roadmap(),
    }
