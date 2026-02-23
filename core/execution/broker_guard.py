# core/execution/broker_guard.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict
import threading
import time


# ---------------------------------------------------------------------
# Decision Object (Immutable)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class BrokerDecision:
    allowed: bool
    freeze: bool
    reason: str


# ---------------------------------------------------------------------
# Broker Guard
# ---------------------------------------------------------------------

class BrokerGuard:
    """
    Institutional Broker Adversarial Immunity Layer.

    Protects against:
    - Latency spikes
    - Missing ACK timeouts
    - Slippage anomalies
    - Heartbeat failures

    Properties:
    - Deterministic
    - Thread-safe
    - Broker-agnostic
    - Freeze-first enforcement
    """

    def __init__(
        self,
        *,
        max_latency_ms: float = 500,
        ack_timeout_seconds: float = 5,
        max_slippage_pct: float = 1.0,
        heartbeat_timeout_seconds: float = 10,
    ) -> None:

        self.max_latency_ms = max_latency_ms
        self.ack_timeout_seconds = ack_timeout_seconds
        self.max_slippage_pct = max_slippage_pct
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds

        self._lock = threading.Lock()
        self._pending_orders: Dict[str, float] = {}
        self._heartbeat_timestamp: Optional[float] = None

    # =============================================================
    # 1️⃣ LATENCY VALIDATION
    # =============================================================

    def validate_latency(self, *, latency_ms: float) -> BrokerDecision:
        if latency_ms > self.max_latency_ms:
            return BrokerDecision(
                allowed=False,
                freeze=True,
                reason="LATENCY_THRESHOLD_EXCEEDED",
            )

        return BrokerDecision(
            allowed=True,
            freeze=False,
            reason="LATENCY_VALID",
        )

    # =============================================================
    # 2️⃣ ACK TRACKING
    # =============================================================

    def register_order(self, order_id: str) -> None:
        with self._lock:
            self._pending_orders[order_id] = time.time()

    def mark_ack_received(self, order_id: str) -> None:
        with self._lock:
            self._pending_orders.pop(order_id, None)

    def validate_ack(self, order_id: str) -> BrokerDecision:
        with self._lock:
            if order_id not in self._pending_orders:
                return BrokerDecision(
                    allowed=True,
                    freeze=False,
                    reason="ACK_VALID",
                )

            created_at = self._pending_orders[order_id]
            elapsed = time.time() - created_at

            if elapsed > self.ack_timeout_seconds:
                return BrokerDecision(
                    allowed=False,
                    freeze=True,
                    reason="ACK_TIMEOUT",
                )

        return BrokerDecision(
            allowed=True,
            freeze=False,
            reason="ACK_PENDING",
        )

    # =============================================================
    # 3️⃣ SLIPPAGE VALIDATION
    # =============================================================

    def validate_slippage(
        self,
        *,
        expected_price: float,
        executed_price: float,
    ) -> BrokerDecision:

        if expected_price <= 0:
            return BrokerDecision(
                allowed=False,
                freeze=True,
                reason="INVALID_EXPECTED_PRICE",
            )

        slippage_pct = abs(executed_price - expected_price) / expected_price * 100

        if slippage_pct > self.max_slippage_pct:
            return BrokerDecision(
                allowed=False,
                freeze=True,
                reason="SLIPPAGE_THRESHOLD_EXCEEDED",
            )

        return BrokerDecision(
            allowed=True,
            freeze=False,
            reason="SLIPPAGE_VALID",
        )

    # =============================================================
    # 4️⃣ HEARTBEAT MONITORING
    # =============================================================

    def update_heartbeat(self) -> None:
        with self._lock:
            self._heartbeat_timestamp = time.time()

    def validate_heartbeat(self) -> BrokerDecision:
        with self._lock:
            if self._heartbeat_timestamp is None:
                return BrokerDecision(
                    allowed=False,
                    freeze=True,
                    reason="HEARTBEAT_MISSING",
                )

            elapsed = time.time() - self._heartbeat_timestamp

            if elapsed > self.heartbeat_timeout_seconds:
                return BrokerDecision(
                    allowed=False,
                    freeze=True,
                    reason="HEARTBEAT_TIMEOUT",
                )

        return BrokerDecision(
            allowed=True,
            freeze=False,
            reason="HEARTBEAT_VALID",
        )