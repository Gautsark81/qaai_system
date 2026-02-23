# core/explainability/summary/summarizer.py
from typing import List
from core.explainability.causality.models import CausalChain


class HumanReadableSummarizer:
    """
    Converts causal chains into concise human-readable summaries.

    NOTE:
    - No inference
    - No judgment
    - No recomputation
    """

    def summarize(self, chain: CausalChain) -> List[str]:
        """
        Returns an ordered list of summary sentences.
        """

        summaries: List[str] = []

        for idx, node in enumerate(chain.nodes, start=1):
            summaries.append(
                f"Step {idx}: {node.description}."
            )

        return summaries
