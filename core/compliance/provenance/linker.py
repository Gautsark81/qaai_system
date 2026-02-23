# core/compliance/provenance/linker.py
from typing import Iterable, List
from core.compliance.provenance.models import (
    EvidenceRef,
    DecisionLink,
    TradeProvenanceChain,
)


class ProvenanceLinker:
    """
    Deterministically links trades to decisions and evidence.

    NOTE:
    - No inference
    - No heuristics
    - Caller provides the relationships
    """

    def build_trade_chain(
        self,
        *,
        trade_id: str,
        decision_links: Iterable[DecisionLink],
    ) -> TradeProvenanceChain:
        # Deterministic ordering by decision_id
        ordered_decisions: List[DecisionLink] = sorted(
            list(decision_links),
            key=lambda d: d.decision_id,
        )

        return TradeProvenanceChain(
            trade_id=trade_id,
            decisions=ordered_decisions,
        )
