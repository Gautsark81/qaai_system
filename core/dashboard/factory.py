# core/dashboard/factory.py

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.dashboard.builder import SnapshotBuilder
from core.dashboard.nulls import (
    EmptyScreeningSnapshot,
    EmptyCapitalSnapshot,
)

from core.watchlist.registry import WatchlistRegistry
from core.strategy_intelligence.core import StrategyIntelligence

# Telemetry rehydration (FINAL, CORRECT)
from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot
from core.execution.telemetry import ExecutionTelemetry
from core.execution.invariant_validator import InvariantResult
from core.execution.telemetry_serializer import deserialize_snapshot


def _load_latest_execution_telemetry_snapshot(
    base_dir: Path,
) -> Optional[ExecutionTelemetrySnapshot]:
    """
    Load the most recent ExecutionTelemetrySnapshot from disk.

    Storage contract:
    - data/telemetry/<execution_id>.jsonl
    - append-only
    - last line = latest snapshot
    """
    try:
        if not base_dir.exists():
            return None

        files = sorted(base_dir.glob("*.jsonl"))
        if not files:
            return None

        latest_file = files[-1]

        with latest_file.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return None

            raw = deserialize_snapshot(lines[-1])

        # ✅ Proper rehydration (objects, not dicts)
        telemetry = ExecutionTelemetry(**raw["telemetry"])
        invariants = InvariantResult(**raw["invariants"])

        return ExecutionTelemetrySnapshot(
            telemetry=telemetry,
            invariants=invariants,
        )

    except Exception:
        # Telemetry must never break dashboard
        return None


def build_dashboard_snapshot():
    """
    Build a read-only CoreSystemSnapshot for the dashboard.

    Invariants:
    - Immutable
    - No execution
    - Telemetry is optional enrichment
    """

    screening_snapshot = EmptyScreeningSnapshot()
    capital_snapshot = EmptyCapitalSnapshot()

    watchlist_registry = WatchlistRegistry()
    strategy_intelligence = StrategyIntelligence(
        strategy_id="DASHBOARD"
    )

    execution_telemetry_snapshot = (
        _load_latest_execution_telemetry_snapshot(
            Path("data/telemetry")
        )
    )

    builder = SnapshotBuilder(
        screening=screening_snapshot,
        watchlist=watchlist_registry,
        strategies=strategy_intelligence,
        capital=capital_snapshot,
        execution_telemetry=execution_telemetry_snapshot,
    )

    return builder.build(
        timestamp=datetime.now(tz=timezone.utc)
    )
