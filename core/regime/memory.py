from collections import defaultdict
from typing import Dict, Tuple


class RegimeMemory:
    """
    Statistical memory of regime survival and transitions.
    No ML. No optimization.
    """

    def __init__(self):
        self.durations: Dict[str, list[int]] = defaultdict(list)
        self.transitions: Dict[Tuple[str, str], int] = defaultdict(int)

    def record_duration(self, regime_key: str, bars: int):
        self.durations[regime_key].append(bars)

    def expected_persistence(self, regime_key: str) -> float:
        values = self.durations.get(regime_key)
        if not values:
            return 0.5
        return min(1.0, sum(values) / (len(values) * 100))

    def record_transition(self, from_key: str, to_key: str):
        self.transitions[(from_key, to_key)] += 1
