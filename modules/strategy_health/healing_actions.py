from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class HealingAction:
    """
    Immutable description of a healing attempt.
    """
    action_type: str
    parameters: Dict[str, Any]
    reason: str
