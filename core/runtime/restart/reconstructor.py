from typing import Optional

from core.capital.usage_ledger.ledger import CapitalUsageLedger
from core.capital.coordination.coordinator import CapitalCoordinator
from core.runtime.restart.models import RestartSnapshot


class RebuiltSystem:
    """
    Immutable container for rebuilt runtime state.
    """
    def __init__(
        self,
        ledger: CapitalUsageLedger,
        coordinator: Optional[CapitalCoordinator],
    ):
        self.ledger = ledger
        self.coordinator = coordinator


class SystemReconstructor:
    """
    Phase 24.3 — Restart / Crash / Resume Determinism
    """

    @staticmethod
    def capture_snapshot(
        ledger: CapitalUsageLedger,
        coordination_decision=None,
        total_capital: float | None = None,
    ) -> RestartSnapshot:
        return RestartSnapshot(
            ledger_entries=ledger.entries(),
            coordination_decision=coordination_decision,
            total_capital=total_capital,
        )

    @staticmethod
    def rebuild(snapshot: RestartSnapshot) -> RebuiltSystem:
        ledger = CapitalUsageLedger.replay(snapshot.ledger_entries)

        coordinator = None
        if snapshot.total_capital is not None:
            coordinator = CapitalCoordinator(
                total_capital=snapshot.total_capital
            )

        return RebuiltSystem(
            ledger=ledger,
            coordinator=coordinator,
        )
