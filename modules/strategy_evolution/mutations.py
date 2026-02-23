from dataclasses import dataclass
from typing import Dict, Any, List
import copy


@dataclass(frozen=True)
class MutationSpec:
    name: str
    reason: str
    max_delta: float           # bounded change (e.g., 0.2 = ±20%)
    applies_to: List[str]      # parameter keys


class MutationOperators:
    """
    Whitelisted, bounded mutation operators.
    """

    def __init__(self, specs: List[MutationSpec]):
        self.specs = specs

    def mutate_parameters(
        self,
        *,
        parameters: Dict[str, Any],
        spec: MutationSpec,
        seed: int,
    ) -> Dict[str, Any]:
        """
        Deterministically mutates parameters according to spec.
        """
        rng = self._rng(seed)
        new_params = copy.deepcopy(parameters)

        for key in spec.applies_to:
            if key not in new_params:
                continue
            value = new_params[key]
            if not isinstance(value, (int, float)):
                continue

            delta = (rng() * 2 - 1) * spec.max_delta
            new_params[key] = type(value)(value * (1 + delta))

        return new_params

    @staticmethod
    def _rng(seed: int):
        # simple deterministic generator
        x = seed or 1

        def next_val():
            nonlocal x
            x = (1103515245 * x + 12345) % (2**31)
            return x / (2**31)

        return next_val
