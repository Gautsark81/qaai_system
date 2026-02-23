import random
from typing import List, Tuple


class CapitalRouter:
    """
    Capital-weighted routing.
    Deterministic given seed.
    """

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)

    def choose_model(
        self,
        weighted_models: List[Tuple[str, float]],
    ) -> str:
        r = self._rng.random()
        cumulative = 0.0

        for model_id, weight in weighted_models:
            cumulative += weight
            if r <= cumulative:
                return model_id

        raise RuntimeError("Invalid capital weights — routing failed")
