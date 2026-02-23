from __future__ import annotations

from typing import Any, Dict, List

from core.v2.research.experiments.base import ResearchExperiment
from core.v2.research.contracts import ResearchExperimentError


class AlphaExperiment(ResearchExperiment):
    """
    Tests simple alpha hypotheses under known market regimes.
    """

    def load(self) -> None:
        meta = self.context.metadata

        if "snapshot_data" not in meta or "returns" not in meta["snapshot_data"]:
            raise ResearchExperimentError("returns missing from snapshot_data")

        if "regime" not in meta:
            raise ResearchExperimentError("regime missing from metadata")

        self._returns: List[float] = list(meta["snapshot_data"]["returns"])
        self._regime: str = meta["regime"]

        if len(self._returns) < 2:
            raise ResearchExperimentError("Insufficient returns for alpha testing")

    def run(self) -> Dict[str, Any]:
        outcomes = self._compute_outcomes(self._returns)

        return {
            "regime": self._regime,
            "outcomes": outcomes,
        }

    def evaluate(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        return raw

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_outcomes(returns: List[float]) -> List[bool]:
        # success = next return positive
        return [r > 0 for r in returns[1:]]
