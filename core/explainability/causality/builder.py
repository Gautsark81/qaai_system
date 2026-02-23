# core/explainability/causality/builder.py
from typing import Iterable, List
from core.explainability.timeline.events import NarrativeEvent
from core.explainability.causality.models import CausalNode, CausalChain


class CausalChainBuilder:
    """
    Builds explicit cause → effect chains from narrative events.

    NOTE:
    - No inference
    - No heuristics
    - Caller provides the intended ordering
    """

    def build_chain(
        self,
        *,
        chain_id: str,
        ordered_events: Iterable[NarrativeEvent],
    ) -> CausalChain:
        nodes: List[CausalNode] = []

        for idx, event in enumerate(ordered_events):
            node = CausalNode(
                event_id=f"{chain_id}:{idx}",
                description=event.description,
                evidence_ref=event.evidence_ref,
            )
            nodes.append(node)

        return CausalChain(
            chain_id=chain_id,
            nodes=nodes,
        )
