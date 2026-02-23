# core/compliance/provenance/models.py
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass(frozen=True)
class EvidenceRef:
    """
    Reference to any persisted evidence (timeline event, causal node, doc).
    """
    ref_type: str
    ref_id: str
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class DecisionLink:
    """
    A decision and the evidence that supports it.
    """
    decision_id: str
    decision_type: str
    evidence: List[EvidenceRef]


@dataclass(frozen=True)
class TradeProvenanceChain:
    """
    Full provenance for a single trade.
    """
    trade_id: str
    decisions: List[DecisionLink]
