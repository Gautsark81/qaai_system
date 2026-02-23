from dataclasses import dataclass
from datetime import datetime


@dataclass
class BridgeState:
    """
    Tracks last rollback action per model for cooldown enforcement.
    """
    last_triggered_at: datetime | None = None
