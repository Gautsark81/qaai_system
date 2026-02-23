from typing import Dict
from core.capital.stress.shock_models import CapitalShock


class CapitalStressEngine:
    """
    Pure stress simulation engine.

    Guarantees:
    - No side effects
    - Deterministic
    - Non-mutating
    """

    def apply_shock(
        self,
        *,
        weights: Dict[str, float],
        shock: CapitalShock,
    ) -> Dict[str, float]:

        stressed = {
            dna: weight * shock.multiplier
            for dna, weight in weights.items()
        }

        total = sum(stressed.values())
        if total > 0:
            stressed = {k: v / total for k, v in stressed.items()}

        return stressed
