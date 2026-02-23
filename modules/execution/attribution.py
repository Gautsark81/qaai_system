from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from modules.execution.events import ExecutionEvent
from modules.execution.analytics import SlippageMetrics
from modules.execution.latency import LatencyMetrics


@dataclass(frozen=True)
class ExecutionAttributionRow:
    """
    Atomic attribution row for a single execution event.
    """
    order_id: str
    symbol: str
    requested_qty: int
    filled_qty: int
    fill_ratio: float

    slippage_abs: Optional[float]
    slippage_bps: Optional[float]

    end_to_end_ms: Optional[float]
    fully_filled: bool


@dataclass(frozen=True)
class ExecutionAttributionReport:
    """
    Aggregated execution attribution report.
    """
    rows: List[ExecutionAttributionRow]

    def summary(self) -> Dict[str, float]:
        """
        High-level rollups for dashboards / logs.
        """
        if not self.rows:
            return {}

        total_orders = len(self.rows)
        avg_fill_ratio = sum(r.fill_ratio for r in self.rows) / total_orders

        slippages = [r.slippage_bps for r in self.rows if r.slippage_bps is not None]
        avg_slippage_bps = sum(slippages) / len(slippages) if slippages else 0.0

        latencies = [r.end_to_end_ms for r in self.rows if r.end_to_end_ms is not None]
        avg_latency_ms = sum(latencies) / len(latencies) if latencies else 0.0

        fill_rate = sum(1 for r in self.rows if r.fully_filled) / total_orders

        return {
            "orders": total_orders,
            "avg_fill_ratio": round(avg_fill_ratio, 4),
            "avg_slippage_bps": round(avg_slippage_bps, 2),
            "avg_latency_ms": round(avg_latency_ms, 2),
            "fill_rate": round(fill_rate, 4),
        }


class ExecutionAttributionEngine:
    """
    Phase 14.4 — Execution Attribution Engine

    Combines:
    - ExecutionEvent (facts)
    - SlippageMetrics (14.2)
    - LatencyMetrics (14.3)

    Produces explainable execution reports.
    """

    @staticmethod
    def build(
        *,
        events: List[ExecutionEvent],
        slippage: Dict[str, SlippageMetrics],
        latency: Dict[str, LatencyMetrics],
    ) -> ExecutionAttributionReport:
        """
        Keys in slippage / latency dicts must be order_id.
        """

        rows: List[ExecutionAttributionRow] = []

        for ev in events:
            slip = slippage.get(ev.order_id)
            lat = latency.get(ev.order_id)

            rows.append(
                ExecutionAttributionRow(
                    order_id=ev.order_id,
                    symbol=ev.symbol,
                    requested_qty=ev.requested_qty,
                    filled_qty=ev.filled_qty,
                    fill_ratio=ev.fill_ratio(),
                    slippage_abs=slip.slippage_abs if slip else None,
                    slippage_bps=slip.slippage_bps if slip else None,
                    end_to_end_ms=lat.end_to_end_ms if lat else None,
                    fully_filled=ev.filled_qty == ev.requested_qty,
                )
            )

        return ExecutionAttributionReport(rows=rows)
