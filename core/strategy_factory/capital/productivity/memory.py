# core/strategy_factory/capital/productivity/memory.py

from dataclasses import dataclass
from typing import Dict, List
from collections import deque


@dataclass(frozen=True)
class ProductivityMemoryConfig:
    window_size: int = 5
    persistence_threshold: int = 3
    hysteresis_strength: float = 0.5  # 0–1 dampening


class ProductivityMemory:

    def __init__(self, config: ProductivityMemoryConfig | None = None):
        self.config = config or ProductivityMemoryConfig()
        self._history: Dict[str, deque] = {}

    def update(self, rotation_map: Dict[str, float]) -> Dict[str, float]:
        """
        Applies rolling memory to rotation map.
        Only reduces allocation if underperformance persists.
        """

        adjusted: Dict[str, float] = {}

        for sid, multiplier in rotation_map.items():

            if sid not in self._history:
                self._history[sid] = deque(maxlen=self.config.window_size)

            underperforming = multiplier < 1.0
            self._history[sid].append(underperforming)

            persistence_count = sum(self._history[sid])

            if persistence_count >= self.config.persistence_threshold:
                dampened = 1.0 - (
                    (1.0 - multiplier) * self.config.hysteresis_strength
                )
                adjusted[sid] = round(dampened, 6)
            else:
                adjusted[sid] = 1.0

        return adjusted

    def snapshot_state(self) -> Dict[str, List[bool]]:
        return {
            sid: list(history)
            for sid, history in self._history.items()
        }