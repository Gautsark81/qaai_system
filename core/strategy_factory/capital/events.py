# core/strategy_factory/capital/events.py

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional


CANONICAL_TIMEZONE = "Asia/Kolkata"
THROTTLE_EVENT_VERSION = "1.0"


def _now_ist() -> datetime:
    """
    Canonical project timezone.
    Must always be IST.
    """
    return datetime.now()


@dataclass(frozen=True)
class ThrottleAuditEvent:
    """
    Immutable audit record for capital throttle decisions.

    Governance Doctrine:
    - Every throttle decision must emit this.
    - No silent throttling.
    - Fully reconstructible.
    """

    event_id: str
    timestamp: datetime
    strategy_id: str
    symbol: str

    requested_capital: float
    approved_capital: float

    throttle_type: str
    throttle_reason: str
    throttle_ratio: float

    capital_state_snapshot: Dict[str, Any]
    regime_snapshot: Optional[Dict[str, Any]] = None

    version: str = field(default=THROTTLE_EVENT_VERSION)

    @staticmethod
    def create(
        strategy_id: str,
        symbol: str,
        requested_capital: float,
        approved_capital: float,
        throttle_type: str,
        throttle_reason: str,
        capital_state_snapshot: Dict[str, Any],
        regime_snapshot: Optional[Dict[str, Any]] = None,
    ) -> "ThrottleAuditEvent":

        if requested_capital <= 0:
            raise ValueError("requested_capital must be > 0")

        if approved_capital < 0:
            raise ValueError("approved_capital must be >= 0")

        ratio = approved_capital / requested_capital

        return ThrottleAuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=_now_ist(),
            strategy_id=strategy_id,
            symbol=symbol,
            requested_capital=requested_capital,
            approved_capital=approved_capital,
            throttle_type=throttle_type,
            throttle_reason=throttle_reason,
            throttle_ratio=ratio,
            capital_state_snapshot=capital_state_snapshot,
            regime_snapshot=regime_snapshot,
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ThrottleAuditEvent":
        return ThrottleAuditEvent(
            event_id=data["event_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            strategy_id=data["strategy_id"],
            symbol=data["symbol"],
            requested_capital=data["requested_capital"],
            approved_capital=data["approved_capital"],
            throttle_type=data["throttle_type"],
            throttle_reason=data["throttle_reason"],
            throttle_ratio=data["throttle_ratio"],
            capital_state_snapshot=data["capital_state_snapshot"],
            regime_snapshot=data.get("regime_snapshot"),
            version=data.get("version", THROTTLE_EVENT_VERSION),
        )