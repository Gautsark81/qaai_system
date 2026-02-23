# core/institution/capital_partition/allocator.py
from typing import Dict
from core.institution.capital_partition.models import (
    CapitalEnvelope,
    CapitalAllocationView,
)


class CapitalPartitionAllocator:
    """
    Enforces portfolio-scoped capital partitions.

    HARD RULE:
    - Capital is non-fungible across portfolios.
    """

    def __init__(self):
        self._envelopes: Dict[str, CapitalEnvelope] = {}
        self._used: Dict[str, float] = {}

    def register_envelope(self, *, envelope: CapitalEnvelope) -> None:
        if envelope.portfolio_id in self._envelopes:
            raise ValueError("capital envelope already registered")
        self._envelopes[envelope.portfolio_id] = envelope
        self._used[envelope.portfolio_id] = 0.0

    def record_usage(self, *, portfolio_id: str, amount: float) -> None:
        if portfolio_id not in self._envelopes:
            raise KeyError("unknown portfolio")

        current = self._used[portfolio_id]
        limit = self._envelopes[portfolio_id].max_capital

        if current + amount > limit:
            raise ValueError("capital envelope exceeded")

        self._used[portfolio_id] = current + amount

    def allocation_view(self, *, portfolio_id: str) -> CapitalAllocationView:
        if portfolio_id not in self._envelopes:
            raise KeyError("unknown portfolio")

        env = self._envelopes[portfolio_id]
        used = self._used[portfolio_id]

        return CapitalAllocationView(
            portfolio_id=portfolio_id,
            max_capital=env.max_capital,
            used_capital=used,
        )
