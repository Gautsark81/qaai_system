from __future__ import annotations
from typing import Dict, Any
import copy
import random


def mutate_indicator_threshold(
    entry: Dict[str, Any],
    delta: float = 5.0,
) -> Dict[str, Any]:
    mutated = copy.deepcopy(entry)

    if mutated.get("type") == "indicator":
        mutated["value"] += random.choice([-delta, delta])

    elif mutated.get("type") in ("AND", "OR"):
        idx = random.randint(0, len(mutated["conditions"]) - 1)
        mutated["conditions"][idx] = mutate_indicator_threshold(
            mutated["conditions"][idx], delta
        )

    return mutated
