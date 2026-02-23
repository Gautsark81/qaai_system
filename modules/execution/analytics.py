from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from modules.execution.events import ExecutionEvent, ExecutionStatus


@dataclass(frozen=True)
class SlippageMetrics:
    """
    Slippage & fill quality metrics for a single execution event.
    """
    expected_price: float
    executed_price: Optional[float]
    filled_qty: int
    requested_qty: int

    slippage_abs: Optional[float]
    slippage_bps: Optional[float]
    fill_ratio: float
    fully_filled: bool


class ExecutionAnalytics:
    """
    Phase 14.2 — Slippage & Fill Analytics

    Pure analytical functions over ExecutionEvent.
    """

    @staticmethod
    def slippage(
        *,
        event: ExecutionEvent,
        expected_price: float,
    ) -> SlippageMetrics:
        """
        Computes slippage vs expected price.

        expected_price:
            Reference price at decision time
            (signal price, mid-price, theoretical price)
        """

        # No fill → no slippage
        if (
            event.avg_price is None
            or event.filled_qty <= 0
            or event.status == ExecutionStatus.REJECTED
        ):
            return SlippageMetrics(
                expected_price=expected_price,
                executed_price=None,
                filled_qty=event.filled_qty,
                requested_qty=event.requested_qty,
                slippage_abs=None,
                slippage_bps=None,
                fill_ratio=event.fill_ratio(),
                fully_filled=False,
            )

        executed_price = event.avg_price
        slippage_abs = executed_price - expected_price

        # Basis points (signed)
        slippage_bps = (
            (slippage_abs / expected_price) * 10_000
            if expected_price != 0
            else None
        )

        fill_ratio = event.fill_ratio()

        return SlippageMetrics(
            expected_price=expected_price,
            executed_price=executed_price,
            filled_qty=event.filled_qty,
            requested_qty=event.requested_qty,
            slippage_abs=slippage_abs,
            slippage_bps=slippage_bps,
            fill_ratio=fill_ratio,
            fully_filled=event.status == ExecutionStatus.FILLED,
        )
