from typing import List
from datetime import datetime

from core.capital.usage_ledger.models import (
    CapitalUsageEntry,
    CapitalEventType,
)


class CapitalUsageLedger:
    """
    Phase 24.1 — Capital Usage Ledger

    LOCKED semantics (derived from tests):

    Used capital per strategy:
    - If NO consumption yet:
        used = allocation - release
    - If ANY consumption exists:
        used = consumption - release

    Properties:
    - Append-only
    - Immutable history
    - Deterministic replay
    - No execution authority
    """

    def __init__(self):
        # Name-mangled to prevent mutation
        self.__entries: List[CapitalUsageEntry] = []

    # ------------------------------------------------------------------
    # Recording (append-only)
    # ------------------------------------------------------------------

    def record_allocation(
        self,
        strategy_id: str,
        amount: float,
        timestamp: datetime,
        reason: str,
    ):
        self.__append(
            CapitalEventType.ALLOCATION,
            strategy_id,
            amount,
            timestamp,
            reason,
        )

    def record_consumption(
        self,
        strategy_id: str,
        amount: float,
        timestamp: datetime,
        reason: str,
    ):
        self.__append(
            CapitalEventType.CONSUMPTION,
            strategy_id,
            amount,
            timestamp,
            reason,
        )

    def record_release(
        self,
        strategy_id: str,
        amount: float,
        timestamp: datetime,
        reason: str,
    ):
        self.__append(
            CapitalEventType.RELEASE,
            strategy_id,
            amount,
            timestamp,
            reason,
        )

    def __append(
        self,
        event_type: CapitalEventType,
        strategy_id: str,
        amount: float,
        timestamp: datetime,
        reason: str,
    ):
        self.__entries.append(
            CapitalUsageEntry(
                event_type=event_type,
                strategy_id=strategy_id,
                amount=amount,
                timestamp=timestamp,
                reason=reason,
            )
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def entries(self):
        return list(self.__entries)

    def total_used_capital(self) -> float:
        return sum(self.used_capital_by_strategy(s) for s in self._strategies())

    def used_capital_by_strategy(self, strategy_id: str) -> float:
        allocation = 0.0
        consumption = 0.0
        release = 0.0

        for e in self.__entries:
            if e.strategy_id != strategy_id:
                continue

            if e.event_type == CapitalEventType.ALLOCATION:
                allocation += e.amount
            elif e.event_type == CapitalEventType.CONSUMPTION:
                consumption += e.amount
            elif e.event_type == CapitalEventType.RELEASE:
                release += e.amount

        if consumption > 0:
            return max(consumption - release, 0.0)
        return max(allocation - release, 0.0)

    def _strategies(self):
        return {e.strategy_id for e in self.__entries}

    # ------------------------------------------------------------------
    # Replay
    # ------------------------------------------------------------------

    @classmethod
    def replay(cls, entries: List[CapitalUsageEntry]) -> "CapitalUsageLedger":
        ledger = cls()
        for e in sorted(entries, key=lambda x: x.timestamp):
            ledger.__entries.append(e)
        return ledger
