from datetime import datetime
from typing import Dict, Any, List

from core.strategy_factory.registry import StrategyRegistry


class LifecycleExplainer:
    """
    Read-only lifecycle explanation engine.

    Explains:
    - Current state
    - How it got there (excluding registration event)
    - Last governance transition
    """

    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    def explain(self, dna: str) -> Dict[str, Any]:
        record = self.registry.get(dna)

        raw_history: List[Dict[str, Any]] = getattr(record, "history", [])

        # 🔒 CRITICAL FIX:
        # Exclude REGISTERED / GENERATED bootstrap events
        lifecycle_history = [
            h for h in raw_history
            if h.get("event") != "REGISTERED"
        ]

        last_transition = lifecycle_history[-1] if lifecycle_history else None

        return {
            "strategy_id": dna,
            "current_state": record.state,
            "lifecycle_history": lifecycle_history,
            "last_transition": last_transition,
            "explanation": self._explain_transition(last_transition),
            "generated_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def _explain_transition(transition: Dict[str, Any] | None) -> str:
        if not transition:
            return "Strategy registered but not yet evaluated."

        frm = transition.get("from")
        to = transition.get("to")

        if to == "BACKTESTED":
            return "Strategy passed historical validation checks."

        if to == "PAPER":
            return "Strategy approved for paper trading under governance rules."

        if to == "LIVE":
            return "Strategy promoted to live trading after meeting performance and risk criteria."

        if to == "FROZEN":
            return "Strategy execution halted due to governance or risk violation."

        return f"Strategy transitioned from {frm} to {to}."
