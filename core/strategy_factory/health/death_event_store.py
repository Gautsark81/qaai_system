from typing import List

from core.strategy_factory.health.death_attribution import DeathAttribution


class DeathEventStore:
    """
    Append-only store for DeathAttribution events.

    This store is:
    - Write-only (record)
    - Read-only via defensive copy (all_events)
    - Deterministic
    - Side-effect free

    Learning, suppression, and resurrection logic
    MUST live outside this class.
    """

    def __init__(self) -> None:
        self._events: List[DeathAttribution] = []

    def record(self, event: DeathAttribution) -> None:
        self._events.append(event)

    def all_events(self) -> List[DeathAttribution]:
        # Return a defensive copy to preserve immutability
        return list(self._events)
