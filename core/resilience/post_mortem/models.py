# core/resilience/post_mortem/models.py
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass(frozen=True)
class PostMortemReport:
    """
    Deterministic, immutable post-mortem report.
    """
    incident_id: str
    summary: str
    timeline: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]
    takeover_events: List[Dict[str, Any]]
    evidence_refs: List[Dict[str, Any]]
