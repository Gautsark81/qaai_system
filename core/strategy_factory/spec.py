from dataclasses import dataclass
from typing import Dict, Tuple, FrozenSet, Iterable


def _freeze(params: Dict) -> FrozenSet[Tuple[str, object]]:
    """
    Deterministically freeze params into a hashable structure.
    Sorting ensures stable DNA across runs.
    """
    return frozenset(sorted(params.items()))


@dataclass(frozen=True)
class StrategySpec:
    """
    Immutable, structural definition of a strategy.

    🔒 Core guarantees:
    - Immutable once created
    - Deterministic hashing / DNA
    - Any change → NEW StrategySpec → NEW DNA
    """

    name: str
    alpha_stream: str
    timeframe: str
    universe: Tuple[str, ...]
    params: FrozenSet[Tuple[str, object]]

    def __init__(
        self,
        name: str,
        alpha_stream: str,
        timeframe: str,
        universe: Iterable[str],
        params: Dict,
    ):
        # Explicit field assignment to preserve immutability
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "alpha_stream", alpha_stream)
        object.__setattr__(self, "timeframe", timeframe)
        object.__setattr__(self, "universe", tuple(universe))
        object.__setattr__(self, "params", _freeze(params))
