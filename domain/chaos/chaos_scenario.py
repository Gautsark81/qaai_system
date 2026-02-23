from dataclasses import dataclass
from typing import List
from domain.chaos.chaos_event import ChaosEvent


@dataclass(frozen=True)
class ChaosScenario:
    name: str
    events: List[ChaosEvent]
