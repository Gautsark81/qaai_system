# core/explainability/timeline/events.py
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class NarrativeEvent:
    """
    A single explainability event.

    NOTE:
    - Read-only
    - Derived from persisted evidence
    """
    timestamp: str
    category: str
    description: str
    evidence_ref: Dict[str, Any]
