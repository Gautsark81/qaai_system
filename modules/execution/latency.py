from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from modules.execution.events import ExecutionEvent, ExecutionStatus


@dataclass(frozen=True)
class LatencyMetrics:
    """
    Latency metrics for a single execution lifecycle.
    All values are in milliseconds.
    """
    decision_to_system_ms: Optional[float]
    system_to_exchange_ms: Optional[float]
    exchange_to_fill_ms: Optional[float]
    end_to_end_ms: Optional[float]
    fully_filled: bool


class ExecutionLatency:
    """
    Phase 14.3 — Latency Attribution

    Computes timing breakdowns using timestamps already present
    in ExecutionEvent. This layer is observational only.
    """

    @staticmethod
    def compute(
        *,
        event: ExecutionEvent,
        decision_ts: datetime,
    ) -> LatencyMetrics:
        """
        decision_ts:
            Timestamp when the trading decision was made
            (signal emission / order intent creation)
        """

        # Defensive: missing timestamps
        if event.system_ts is None or event.exchange_ts is None:
            return LatencyMetrics(
                decision_to_system_ms=None,
                system_to_exchange_ms=None,
                exchange_to_fill_ms=None,
                end_to_end_ms=None,
                fully_filled=False,
            )

        # Segment 1: decision → system (order creation)
        decision_to_system_ms = (
            (event.system_ts - decision_ts).total_seconds() * 1000.0
        )

        # Segment 2: system → exchange
        system_to_exchange_ms = (
            (event.exchange_ts - event.system_ts).total_seconds() * 1000.0
        )

        # Segment 3: exchange → fill (if filled)
        if event.status in {ExecutionStatus.FILLED, ExecutionStatus.PARTIAL}:
            exchange_to_fill_ms = 0.0
        else:
            exchange_to_fill_ms = None

        # End-to-end latency
        end_to_end_ms = (
            (event.exchange_ts - decision_ts).total_seconds() * 1000.0
        )

        return LatencyMetrics(
            decision_to_system_ms=decision_to_system_ms,
            system_to_exchange_ms=system_to_exchange_ms,
            exchange_to_fill_ms=exchange_to_fill_ms,
            end_to_end_ms=end_to_end_ms,
            fully_filled=event.status == ExecutionStatus.FILLED,
        )
