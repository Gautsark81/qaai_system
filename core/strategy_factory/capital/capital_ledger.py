from __future__ import annotations

from typing import List
from datetime import datetime

from core.strategy_factory.capital.capital_ledger_models import (
    CapitalUsageEvent,
)


class CapitalUsageLedger:
    """
    Append-only capital usage ledger.

    Deterministic.
    Replay-safe.
    Immutable history.
    """

    def __init__(self) -> None:
        self._events: List[CapitalUsageEvent] = []

    # ----------------------------------------------------------
    # Append Event
    # ----------------------------------------------------------

    def record(
        self,
        *,
        strategy_dna: str,
        requested_capital: float,
        approved_capital: float,
        deployed_capital: float,
        now: datetime,
    ) -> CapitalUsageEvent:

        if requested_capital < 0:
            raise ValueError("requested_capital must be >= 0")

        if approved_capital < 0:
            raise ValueError("approved_capital must be >= 0")

        if deployed_capital < 0:
            raise ValueError("deployed_capital must be >= 0")

        event = CapitalUsageEvent(
            strategy_dna=strategy_dna,
            requested_capital=requested_capital,
            approved_capital=approved_capital,
            deployed_capital=deployed_capital,
            created_at=now,
        )

        self._events.append(event)
        return event

    # ----------------------------------------------------------
    # Read-only Access
    # ----------------------------------------------------------

    @property
    def events(self) -> List[CapitalUsageEvent]:
        return list(self._events)

    # ----------------------------------------------------------
    # Aggregations
    # ----------------------------------------------------------

    def total_requested(self) -> float:
        return sum(e.requested_capital for e in self._events)

    def total_approved(self) -> float:
        return sum(e.approved_capital for e in self._events)

    def total_deployed(self) -> float:
        return sum(e.deployed_capital for e in self._events)

    def utilization_ratio(self) -> float:
        approved = self.total_approved()
        if approved == 0:
            return 0.0
        return self.total_deployed() / approved