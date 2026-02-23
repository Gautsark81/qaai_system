from dataclasses import dataclass
from typing import Dict
from .incident_types import IncidentType


@dataclass(frozen=True)
class IncidentRecord:
    """
    Immutable incident record.

    Used for:
    - audit
    - replay
    - post-mortem reconstruction
    """

    incident_type: IncidentType
    timestamp: int
    scope: str
    summary: Dict[str, str]
