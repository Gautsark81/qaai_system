from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------
# BACKWARD-COMPATIBILITY DECISION CONTRACT
# ---------------------------------------------------------------------
class BrokerDecision:
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


# ---------------------------------------------------------------------
# CANONICAL BROKER RESPONSE (NO RAW PAYLOAD)
# ---------------------------------------------------------------------
@dataclass(frozen=True, init=False)
class BrokerResponse:
    """
    Canonical, deterministic broker response.

    Guarantees:
    - No raw broker payload
    - Deterministic serialization
    - Replay-safe
    - Hash-anchorable
    """

    broker: str
    order_id: Optional[str]
    status: str

    filled_quantity: int
    avg_price: float

    timestamp: datetime
    rejection_reason: Optional[str]

    # --------------------------------------------------
    # NORMALIZING CONSTRUCTOR
    # --------------------------------------------------
    def __init__(
        self,
        *,
        # governance style
        decision: Optional[str] = None,
        average_price: Optional[float] = None,
        broker_reference: Optional[str] = None,

        # canonical style
        broker: Optional[str] = None,
        status: Optional[str] = None,
        avg_price: Optional[float] = None,

        # shared
        filled_quantity: int,
        order_id: Optional[str],
        timestamp: datetime,
        rejection_reason: Optional[str] = None,
    ):
        final_broker = broker_reference or broker
        if final_broker is None:
            raise TypeError("broker or broker_reference is required")

        # --------------------------------------------------
        # STATUS NORMALIZATION (CRITICAL FIX)
        # --------------------------------------------------
        if status is None:
            if decision is None:
                raise TypeError("Either status or decision must be provided")

            if decision == BrokerDecision.ACCEPTED and filled_quantity > 0:
                status = "FILLED"
            else:
                # 🔒 Explicit business rejection, not terminal failure
                status = "REJECTED"

        final_price = (
            avg_price
            if avg_price is not None
            else average_price
            if average_price is not None
            else 0.0
        )

        object.__setattr__(self, "broker", final_broker)
        object.__setattr__(self, "order_id", order_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "filled_quantity", filled_quantity)
        object.__setattr__(self, "avg_price", final_price)
        object.__setattr__(self, "timestamp", timestamp)
        object.__setattr__(self, "rejection_reason", rejection_reason)

    # --------------------------------------------------
    # LEGACY PROJECTIONS
    # --------------------------------------------------
    @property
    def decision(self) -> str:
        if self.status in ("FILLED", "PARTIALLY_FILLED", "ACCEPTED"):
            return BrokerDecision.ACCEPTED
        return BrokerDecision.REJECTED

    @property
    def average_price(self) -> float:
        return self.avg_price

    @property
    def broker_reference(self) -> str:
        return self.broker

    # --------------------------------------------------
    # DETERMINISTIC HASH
    # --------------------------------------------------
    @property
    def response_hash(self) -> str:
        return broker_response_hash(self)


# ---------------------------------------------------------------------
# HASHING
# ---------------------------------------------------------------------
def broker_response_hash(response: BrokerResponse) -> str:
    payload = json.dumps(
        asdict(response),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


__all__ = [
    "BrokerResponse",
    "BrokerDecision",
    "broker_response_hash",
]
