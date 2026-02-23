# core/execution/paper_broker.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from core.execution.broker import Broker, BrokerFill
from core.execution.execution_intent import ExecutionIntent


# -------------------------------------------------
# Deterministic Pricing Policy (Pure Function)
# -------------------------------------------------

@dataclass(frozen=True)
class DeterministicPricingPolicy:
    """
    Deterministic pricing inputs for paper execution.

    All values are explicit and testable.
    No randomness. No IO.
    """

    base_price: float
    slippage_per_unit: float
    flat_fee: float


# -------------------------------------------------
# Paper Broker
# -------------------------------------------------

class PaperBroker(Broker):
    """
    Deterministic paper broker.

    - No IO
    - No capital mutation
    - No telemetry
    - Purely synchronous
    """

    def __init__(
        self,
        *,
        broker_name: str = "PAPER",
        pricing_policy: DeterministicPricingPolicy,
        execution_id_factory: Callable[[], str],
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._broker_name = broker_name
        self._pricing = pricing_policy
        self._execution_id_factory = execution_id_factory
        self._clock = clock or (lambda: datetime.now(tz=timezone.utc))

    # -------------------------------------------------
    # Broker Contract
    # -------------------------------------------------

    def submit_order(
        self,
        *,
        intent: ExecutionIntent,
    ) -> BrokerFill:
        """
        Deterministically 'fills' the order immediately.
        """

        execution_id = self._execution_id_factory()
        filled_at = self._clock()

        quantity = float(intent.quantity)

        # -------------------------------
        # Deterministic pricing
        # -------------------------------
        slippage = self._pricing.slippage_per_unit * quantity
        fees = self._pricing.flat_fee
        fill_price = self._pricing.base_price + (
            slippage / max(quantity, 1.0)
        )

        return BrokerFill(
            execution_id=execution_id,
            symbol=intent.symbol,
            side=intent.side,
            quantity=quantity,
            fill_price=fill_price,
            fees=fees,
            slippage=slippage,
            filled_at=filled_at,
            broker_name=self._broker_name,
            is_paper=True,
        )
