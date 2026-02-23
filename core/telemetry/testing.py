from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List


@dataclass(frozen=True)
class ExecutionTelemetryEvent:
    run_id: str
    sequence: int
    strategy_id: str | None = None
    symbol: str | None = None
    side: str | None = None
    qty: int | None = None


class _EventView:
    """
    Callable + list-like façade.

    Supports:
    - sink.events()
    - len(sink.events)
    - sink.events[-1]
    - iteration
    """

    def __init__(self, backing: List[ExecutionTelemetryEvent]):
        self._backing = backing

    def __call__(self) -> List[ExecutionTelemetryEvent]:
        return list(self._backing)

    def __len__(self) -> int:
        return len(self._backing)

    def __iter__(self) -> Iterator[ExecutionTelemetryEvent]:
        return iter(self._backing)

    def __getitem__(self, idx):
        return self._backing[idx]


class InMemoryTelemetrySink:
    """
    Test-only telemetry sink.

    🔒 CONTRACT (HARD-LOCKED):
    - sink.events() works
    - len(sink.events) works
    - ordering preserved
    - immutable snapshots
    """

    def __init__(self):
        self._events: List[ExecutionTelemetryEvent] = []
        self.events = _EventView(self._events)

    # --------------------------------------------------
    # EMISSION
    # --------------------------------------------------
    def emit_execution(self, payload: Dict[str, Any]) -> None:
        self._events.append(
            ExecutionTelemetryEvent(
                run_id=payload["run_id"],
                sequence=payload["sequence"],
                strategy_id=payload.get("strategy_id"),
                symbol=payload.get("symbol"),
                side=payload.get("side"),
                qty=payload.get("qty"),
            )
        )

    def clear(self) -> None:
        self._events.clear()
