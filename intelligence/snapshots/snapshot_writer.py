from datetime import datetime
from copy import deepcopy
from typing import Optional, Any
import uuid

from .snapshot_models import StrategyMetricsSnapshot
from .json_storage import JsonLineStorage


def _safe(value: Any):
    if value is None:
        return None
    if isinstance(value, (int, float, str, bool)):
        return value
    if isinstance(value, list):
        return [_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: _safe(v) for k, v in value.items()}
    return repr(value)


class SnapshotWriter:
    """
    Phase-19 Snapshot Writer
    """

    def __init__(self, storage: Optional[JsonLineStorage] = None):
        self.storage = storage
        self._buffer = []

    # --------------------------------------------------
    def write(self, payload: dict) -> StrategyMetricsSnapshot:
        snapshot = StrategyMetricsSnapshot(
            snapshot_id=str(uuid.uuid4()),
            strategy_id=payload["strategy_id"],
            strategy_version=payload.get("strategy_version", "unknown"),
            created_at=datetime.utcnow(),
            window_start=payload["window_start"],
            window_end=payload["window_end"],
            window_type=payload.get("window_type", "ROLLING"),
            stage=payload.get("stage", "BACKTEST"),
            ssr=float(payload.get("ssr", 0.0)),
            total_trades=int(payload.get("total_trades", 0)),
            successful_trades=int(payload.get("successful_trades", 0)),
            win_rate=float(payload.get("win_rate", 0.0)),
            expectancy=float(payload.get("expectancy", 0.0)),
            max_drawdown=float(payload.get("max_drawdown", 0.0)),
            symbol_metrics=_safe(payload.get("symbol_metrics", {})),
            regime_metrics=_safe(payload.get("regime_metrics", {})),
            risk_events=_safe(payload.get("risk_events", [])),
            governance_flags=_safe(payload.get("governance_flags", [])),
            notes=str(payload.get("notes", "")),
        )

        snapshot = deepcopy(snapshot)

        if self.storage:
            self.storage.write(snapshot)
        else:
            self._buffer.append(snapshot)

        return snapshot
