# core/explainability/causality/models.py
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass(frozen=True)
class CausalNode:
    """
    One step in a cause → effect chain.
    """
    event_id: str
    description: str
    evidence_ref: Dict[str, Any]


@dataclass(frozen=True)
class CausalChain:
    """
    Ordered causal explanation.
    """
    chain_id: str
    nodes: List[CausalNode]
