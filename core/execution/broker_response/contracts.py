from enum import Enum
from dataclasses import dataclass
from typing import Optional


class BrokerDecision(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PARTIAL_FILL = "PARTIAL_FILL"
    TRANSIENT_FAILURE = "TRANSIENT_FAILURE"
    UNKNOWN_STATE = "UNKNOWN_STATE"


@dataclass(frozen=True)
class BrokerResponseContract:
    """
    Immutable, replay-safe broker response.
    No execution authority.
    """

    execution_id: str
    broker: str
    decision: BrokerDecision

    broker_order_id: Optional[str] = None
    filled_quantity: Optional[int] = None
    avg_fill_price: Optional[float] = None

    failure_reason: Optional[str] = None
    raw_snapshot_hash: Optional[str] = None
