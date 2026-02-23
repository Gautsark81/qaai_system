# core/institution/memory/models.py
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class OrgMemoryRecord:
    """
    Immutable organization-level memory entry.
    """
    record_id: str
    portfolio_id: str
    category: str
    summary: str
    details: Dict[str, Any]
