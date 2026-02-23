from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass(frozen=True)
class ObservabilityEvent:
    """
    Base structured event.
    """
    event_type: str
    source: str
    model_id: str
    payload: Dict[str, Any]
    timestamp: datetime
