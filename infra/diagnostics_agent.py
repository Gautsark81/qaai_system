from __future__ import annotations

"""
Diagnostics agent that listens to EventBus events and logs a compact
human-readable summary for debugging.

This is optional and not used by tests. You can use it in:
- sandbox / paper runs
- local live test runs
"""

from typing import Any

from infra.event_bus import Event, get_global_event_bus
from infra.logging import get_logger


logger = get_logger("infra.diagnostics_agent")


class DiagnosticsAgent:
    """
    Subscribes to:
    - live.cycle.start
    - live.cycle.success
    - live.cycle.failure
    - portfolio.snapshot
    """

    def __init__(self) -> None:
        self._bus = get_global_event_bus()
        self._logger = logger  # <--- add this line

    def start(self) -> None:
        """
        Register all subscriptions.
        Call this once during app startup.
        """
        self._bus.subscribe("live.cycle.start", self.on_cycle_start)
        self._bus.subscribe("live.cycle.success", self.on_cycle_success)
        self._bus.subscribe("live.cycle.failure", self.on_cycle_failure)
        self._bus.subscribe("portfolio.snapshot", self.on_portfolio_snapshot)

        logger.info("DiagnosticsAgent: subscribed to live events")

    # ------------------------------------------------------------------ #
    # Handlers
    # ------------------------------------------------------------------ #

    def on_cycle_start(self, event: Event) -> None:
        idx = event.payload.get("cycle_index")
        meta = event.metadata or {}
        logger.debug(
            "Diagnostics: cycle start",
            extra={
                "cycle_index": idx,
                "strategy_id": meta.get("strategy_id"),
                "run_id": meta.get("run_id"),
                "sleep": meta.get("loop_sleep_seconds"),
            },
        )

    def on_cycle_success(self, event: Event) -> None:
        idx = event.payload.get("cycle_index")
        logger.debug(
            "Diagnostics: cycle success",
            extra={
                "cycle_index": idx,
                "num_orders": event.payload.get("num_orders"),
                "num_active_orders": event.payload.get("num_active_orders"),
                "num_fills": event.payload.get("num_fills"),
                "num_errors": event.payload.get("num_errors"),
            },
        )

    def on_cycle_failure(self, event: Event) -> None:
        idx = event.payload.get("cycle_index")
        logger.warning(
            "Diagnostics: cycle failure",
            extra={
                "cycle_index": idx,
                "error_type": event.payload.get("error_type"),
                "error_message": event.payload.get("error_message"),
            },
        )

    def on_portfolio_snapshot(self, event: "Event") -> None:
        """
        Handle portfolio.snapshot events.

        Works with either:
        - dict-like snapshots: {"positions": {...}, ...}
        - object snapshots: PortfolioSnapshot with a .positions attribute
        """
        # Be defensive: event may or may not have payload/metadata attributes
        payload = getattr(event, "payload", {}) or {}
        metadata = getattr(event, "metadata", {}) or {}

        snapshot = payload.get("snapshot")
        equity = metadata.get("equity")
        cash = metadata.get("cash")

        num_positions = None
        snapshot_type = type(snapshot).__name__

        try:
            positions = None

            # Case 1: dict-like snapshot
            if isinstance(snapshot, dict):
                positions = snapshot.get("positions") or {}

            # Case 2: object with .positions attribute (PortfolioSnapshot)
            else:
                positions = getattr(snapshot, "positions", None)

            if positions is not None and hasattr(positions, "__len__"):
                num_positions = len(positions)

        except Exception:
            # Diagnostics must never throw – just fall back to None
            num_positions = None

        # Low-volume info-level diagnostic; feel free to change to DEBUG later
        self._logger.info(
            "Diagnostics: portfolio snapshot",
            extra={
                "equity": equity,
                "cash": cash,
                "num_positions": num_positions,
                "snapshot_type": snapshot_type,
            },
        )
