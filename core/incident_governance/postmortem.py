from dataclasses import dataclass
from typing import Dict
from .incident_record import IncidentRecord


@dataclass(frozen=True)
class PostMortemHook:
    """
    Post-mortem evidence hook.

    This object exists to:
    - reference incident records
    - bind them to later analysis
    """

    incident: IncidentRecord
    notes: Dict[str, str]
