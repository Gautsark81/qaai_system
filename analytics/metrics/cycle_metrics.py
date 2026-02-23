from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .base import MetricContext, MetricsSink, LoggingMetricsSink, monotonic_ns


# ---------------------------------------------------------------------------
# Legacy JSONL sink – kept for tests + simple deployments
# ---------------------------------------------------------------------------

DEFAULT_METRICS_PATH = Path("logs") / "cycle_metrics.jsonl"


def _ensure_parent_dir(path: Path) -> None:
    """
    Ensure the parent directory for the given path exists.

    This is a small helper that tests monkeypatch to simulate failures.
    """
    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


def _json_safe(data: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Make payload JSON-serialisable by converting non-JSON-able values
    to their repr() string.

    This matches the expectations in tests/test_cycle_metrics_sink.py.
    """
    safe: Dict[str, Any] = {}
    for k, v in data.items():
        try:
            json.dumps(v)
            safe[k] = v
        except TypeError:
            safe[k] = repr(v)
    return safe


def record_cycle_metrics(
    payload: Mapping[str, Any],
    *,
    store_path: Optional[Path] = None,
) -> None:
    """
    Very small JSONL sink used by tests + simple deployments.

    Behaviour expected by tests:
    - Writes a single JSON object per line.
    - Adds standard fields:
        event = "TRADING_CYCLE"
        ts    = ISO-8601 UTC timestamp
    - Includes custom payload fields.
    - Converts non-JSON-able values to strings.
    - Fails soft on directory / I/O errors (never raises).

    See tests/test_cycle_metrics_sink.py.
    """
    path = store_path or DEFAULT_METRICS_PATH

    # Standard fields
    base_record: Dict[str, Any] = {
        "event": "TRADING_CYCLE",
        "ts": datetime.now(timezone.utc).isoformat(),
    }

    try:
        _ensure_parent_dir(path)

        full_payload = {**base_record, **_json_safe(dict(payload))}
        with path.open("a", encoding="utf-8") as f:
            json.dump(full_payload, f, sort_keys=True)
            f.write("\n")
    except Exception:
        # Metrics must never break the trading loop or tests.
        return


# ---------------------------------------------------------------------------
# New metrics spine – CycleMetricsRecorder
# ---------------------------------------------------------------------------


@dataclass
class CycleSnapshot:
    cycle_id: str
    cycle_type: str = "live_loop"  # e.g. "live_loop", "backtest_step"
    started_ns: int = field(default_factory=monotonic_ns)
    extra: Dict[str, Any] = field(default_factory=dict)


class CycleMetricsRecorder:
    """
    Records metrics per event-loop cycle.

    Typical usage in a live engine loop:

        recorder = CycleMetricsRecorder()
        ctx = MetricContext(env="live", strategy_id="strat_1", run_id=run_id)

        while True:
            cycle = recorder.on_cycle_start(cycle_id=str(cycle_index), context=ctx)
            try:
                # ... trading logic ...
                recorder.on_cycle_success(
                    cycle=cycle,
                    context=ctx,
                    num_orders=...,
                    num_fills=...,
                )
            except Exception as exc:
                recorder.on_cycle_failure(cycle=cycle, context=ctx, exc=exc)
                raise

    This class is deliberately *stateless* beyond simple snapshots so it is easy
    to use across async/sync code and even from multiple tasks.
    """

    def __init__(self, sink: Optional[MetricsSink] = None) -> None:
        self._sink: MetricsSink = sink or LoggingMetricsSink()

    # ------------------------------------------------------------------ #
    # Cycle lifecycle
    # ------------------------------------------------------------------ #

    def on_cycle_start(
        self,
        cycle_id: str,
        context: Optional[MetricContext] = None,
        *,
        cycle_type: str = "live_loop",
        extra: Optional[Dict[str, Any]] = None,
    ) -> CycleSnapshot:
        snapshot = CycleSnapshot(
            cycle_id=cycle_id,
            cycle_type=cycle_type,
            extra=extra or {},
        )

        payload: Dict[str, Any] = {
            "phase": "start",
            "cycle_id": snapshot.cycle_id,
            "cycle_type": snapshot.cycle_type,
            "started_ns": snapshot.started_ns,
        }
        if snapshot.extra:
            payload["tags"] = snapshot.extra
        if context:
            payload["context"] = context.to_dict()

        self._safe_emit("cycle", payload)
        return snapshot

    def on_cycle_success(
        self,
        cycle: CycleSnapshot,
        context: Optional[MetricContext] = None,
        *,
        num_orders: int = 0,
        num_active_orders: int = 0,
        num_fills: int = 0,
        num_errors: int = 0,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        finished_ns = monotonic_ns()
        duration_ns = max(0, finished_ns - cycle.started_ns)

        payload: Dict[str, Any] = {
            "phase": "success",
            "cycle_id": cycle.cycle_id,
            "cycle_type": cycle.cycle_type,
            "duration_ns": duration_ns,
            "num_orders": int(num_orders),
            "num_active_orders": int(num_active_orders),
            "num_fills": int(num_fills),
            "num_errors": int(num_errors),
        }

        tags: Dict[str, Any] = {}
        if cycle.extra:
            tags.update(cycle.extra)
        if extra:
            tags.update(extra)
        if tags:
            payload["tags"] = tags

        if context:
            payload["context"] = context.to_dict()

        self._safe_emit("cycle", payload)

    def on_cycle_failure(
        self,
        cycle: CycleSnapshot,
        context: Optional[MetricContext] = None,
        *,
        exc: BaseException,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        finished_ns = monotonic_ns()
        duration_ns = max(0, finished_ns - cycle.started_ns)

        payload: Dict[str, Any] = {
            "phase": "failure",
            "cycle_id": cycle.cycle_id,
            "cycle_type": cycle.cycle_type,
            "duration_ns": duration_ns,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        }

        tags: Dict[str, Any] = {}
        if cycle.extra:
            tags.update(cycle.extra)
        if extra:
            tags.update(extra)
        if tags:
            payload["tags"] = tags

        if context:
            payload["context"] = context.to_dict()

        self._safe_emit("cycle", payload)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _safe_emit(self, name: str, payload: Dict[str, Any]) -> None:
        try:
            self._sink.emit(name, payload)
        except Exception:  # noqa: BLE001
            # Fail-closed – metrics must never bring down trading
            pass
