# core/resilience/post_mortem/builder.py
from typing import List, Dict, Any
from core.resilience.post_mortem.models import PostMortemReport


class PostMortemBuilder:
    """
    Builds an automated post-mortem report from persisted evidence.

    NOTE:
    - No inference
    - No mutation
    - Deterministic ordering only
    """

    def build(
        self,
        *,
        incident_id: str,
        summary: str,
        timeline_events: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
        takeover_events: List[Dict[str, Any]],
        evidence_refs: List[Dict[str, Any]],
    ) -> PostMortemReport:
        return PostMortemReport(
            incident_id=incident_id,
            summary=summary,
            timeline=sorted(timeline_events, key=lambda e: e.get("timestamp", "")),
            decisions=sorted(decisions, key=lambda d: d.get("decision_id", "")),
            takeover_events=sorted(takeover_events, key=lambda t: t.get("authority", "")),
            evidence_refs=sorted(evidence_refs, key=lambda e: e.get("ref_id", "")),
        )
