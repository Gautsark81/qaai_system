# core/dashboard/builder.py

from datetime import datetime
from typing import Any, Optional

from core.dashboard.snapshot import CoreSystemSnapshot
from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot


class SnapshotBuilder:
    """
    Pure wiring adapter.

    - Reads finalized core components
    - Performs NO recomputation
    - Performs NO IO
    - Produces immutable CoreSystemSnapshot
    """

    def __init__(
        self,
        *,
        screening: Any,
        watchlist: Any,
        strategies: Any,
        capital: Any,
        execution_telemetry: Optional[ExecutionTelemetrySnapshot] = None,
    ) -> None:
        if any(x is None for x in (screening, watchlist, strategies, capital)):
            raise TypeError("All snapshot components must be provided")

        self._screening = screening
        self._watchlist = watchlist
        self._strategies = strategies
        self._capital = capital
        self._execution_telemetry = execution_telemetry

    def build(self, *, timestamp: datetime) -> CoreSystemSnapshot:
        """
        Build an immutable CoreSystemSnapshot.
        """
        return CoreSystemSnapshot(
            timestamp=timestamp,
            system_health=self._derive_system_health(),
            screening=self._screening,
            watchlist=self._watchlist,
            strategies=self._strategies,
            capital=self._capital,
            alerts=(),
            execution_telemetry_snapshot=self._execution_telemetry,
        )

    def _derive_system_health(self) -> str:
        unstable = getattr(self._strategies, "unstable", ())
        degrading = getattr(self._strategies, "degrading", ())

        if unstable:
            return "UNSTABLE"
        if degrading:
            return "DEGRADING"
        return "HEALTHY"
