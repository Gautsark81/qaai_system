from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from core.ssr.contracts.components import SSRComponentScore
from core.strategy_health.contracts.enums import HealthStatus


@dataclass(frozen=True)
class StrategyHealthReport:
    """
    Phase 15.1 — Strategy Health Report (READ-ONLY)

    Pure evidence aggregation.
    Snapshot, SSR, and regime are treated as opaque inputs.
    """

    strategy_dna: str
    health_snapshot: Any
    stability_score: SSRComponentScore
    regime: Optional[Any] = None

    # ------------------------------------------------------------------
    # Derived Read-Only Signals
    # ------------------------------------------------------------------

    @property
    def is_healthy(self) -> bool:
        return getattr(self.health_snapshot, "status", None) == HealthStatus.HEALTHY

    @property
    def promotion_ready(self) -> bool:
        if not self.is_healthy:
            return False

        if self.regime is not None:
            is_favorable = getattr(self.regime, "is_favorable", True)
            if not is_favorable:
                return False

        return True

    # ------------------------------------------------------------------
    # Evidence Export
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_dna": self.strategy_dna,
            "health": (
                self.health_snapshot.to_dict()
                if hasattr(self.health_snapshot, "to_dict")
                else None
            ),
            "stability_score": {
                "name": self.stability_score.name,
                "score": self.stability_score.score,
                "weight": self.stability_score.weight,
                "metrics": self.stability_score.metrics,
            },
            "regime": (
                self.regime.to_dict()
                if self.regime is not None and hasattr(self.regime, "to_dict")
                else None
            ),
            "promotion_ready": self.promotion_ready,
        }
