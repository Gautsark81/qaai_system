# core/execution/broker.py

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from core.execution.execution_intent import ExecutionIntent


# -------------------------------------------------
# Broker Fill (Pure Data)
# -------------------------------------------------

@dataclass(frozen=True)
class BrokerFill:
    """
    Result of submitting an order to a broker.

    This is a PURE data object.
    No capital mutation.
    No telemetry.
    No side effects.
    """

    execution_id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    quantity: float

    fill_price: float
    fees: float
    slippage: float

    filled_at: datetime
    broker_name: str
    is_paper: bool


# -------------------------------------------------
# Broker Interface (Contract)
# -------------------------------------------------

class Broker(ABC):
    """
    Abstract broker interface.

    ExecutionEngine MUST depend only on this interface,
    never on concrete broker implementations.
    """

    @abstractmethod
    def submit_order(
        self,
        *,
        intent: ExecutionIntent,
    ) -> BrokerFill:
        """
        Submit an execution intent to the broker.

        Must be:
        - Deterministic (for paper broker)
        - Synchronous (for now)
        - Side-effect free except returning BrokerFill

        Raises:
        - BrokerRejectError (future phase)
        """
        raise NotImplementedError
