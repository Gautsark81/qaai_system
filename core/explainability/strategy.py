from typing import Dict, Any

from core.strategy_factory.registry import StrategyRegistry
from core.regime.health import strategy_health_snapshot


class StrategyExplainer:
    """
    Read-only explainability engine.

    PURPOSE:
    - Explain *what* a strategy is
    - Explain *why* it is in its current state
    - NEVER mutate registry
    - NEVER compute signals
    """

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    # =====================================================
    # CORE EXPLANATION (dict-based, test-safe)
    # =====================================================

    def explain(self, dna: str) -> Dict[str, Any]:
        record = self.registry.get(dna)
        spec = record.spec  # 🔒 canonical source of identity metadata

        health = strategy_health_snapshot(record)

        notes = (
            "Strategy operating within expected regime bounds"
            if health.get("healthy", True)
            else "Strategy degraded due to regime mismatch"
        )

        return {
            # --- identity ---
            "strategy_id": dna,
            "alpha_stream": spec.alpha_stream,
            "timeframe": spec.timeframe,
            "universe": spec.universe,

            # --- state ---
            "state": record.state,
            "ssr": record.ssr,

            # --- health ---
            "health": health,

            # --- explanation ---
            "notes": notes,
        }

    # =====================================================
    # DASHBOARD SNAPSHOT
    # =====================================================

    def snapshot(self) -> Dict[str, Any]:
        """
        Dashboard-safe explainability projection.
        """

        traces: Dict[str, Any] = {
            dna: self.explain(dna)
            for dna in self.registry.all().keys()
        }

        return {
            "strategy_traces": traces,
            "system_notes": {
                "explainability_version": "E-1",
                "deterministic": True,
                "mutates_state": False,
            },
        }
