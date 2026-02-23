# core/execution/runtime_capital_guard.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import threading


# ---------------------------------------------------------------------
# Decision Object (Immutable)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class CapitalGuardDecision:
    allowed: bool
    freeze: bool
    reason: str


# ---------------------------------------------------------------------
# Runtime Capital Guard (Concurrency-Safe)
# ---------------------------------------------------------------------

class RuntimeCapitalGuard:
    """
    Institutional Runtime Capital Guard.

    Guarantees:
    - Atomic capital validation under concurrency
    - Reservation before broker call
    - Drift validation after fill
    - Idempotency enforcement
    - Reconciliation mismatch freeze
    - Kill switch precedence

    Properties:
    - Deterministic
    - Thread-safe
    - Broker-agnostic
    - Strategy-agnostic
    - Does NOT mutate exposure objects
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._reserved_global = 0.0
        self._reserved_strategy = 0.0
        self._reserved_symbol = 0.0

    # =============================================================
    # PRE-EXECUTION VALIDATION (ATOMIC + RESERVATION)
    # =============================================================

    def validate_pre_execution(
        self,
        *,
        envelope,
        exposure,
        proposed_order_value: float,
        kill_switch: Optional[object],
    ) -> CapitalGuardDecision:
        """
        Atomically validate and reserve capital before broker call.
        """

        # Kill switch always takes precedence
        if kill_switch and getattr(kill_switch, "is_triggered", None):
            if kill_switch.is_triggered():
                return CapitalGuardDecision(
                    allowed=False,
                    freeze=True,
                    reason="KILL_SWITCH_TRIGGERED",
                )

        with self._lock:
            projected_global = (
                exposure.global_exposure
                + self._reserved_global
                + proposed_order_value
            )

            projected_strategy = (
                exposure.strategy_exposure
                + self._reserved_strategy
                + proposed_order_value
            )

            projected_symbol = (
                exposure.symbol_exposure
                + self._reserved_symbol
                + proposed_order_value
            )

            if projected_global > envelope.global_cap:
                return CapitalGuardDecision(False, True, "GLOBAL_CAP_BREACH")

            if projected_strategy > envelope.strategy_cap:
                return CapitalGuardDecision(False, True, "STRATEGY_CAP_BREACH")

            if projected_symbol > envelope.symbol_cap:
                return CapitalGuardDecision(False, True, "SYMBOL_CAP_BREACH")

            # Atomic reservation
            self._reserved_global += proposed_order_value
            self._reserved_strategy += proposed_order_value
            self._reserved_symbol += proposed_order_value

        return CapitalGuardDecision(True, False, "PRE_EXECUTION_VALID")

    # =============================================================
    # POST-FILL VALIDATION (RELEASE RESERVATION + DRIFT CHECK)
    # =============================================================

    def validate_post_fill(
        self,
        *,
        envelope,
        updated_exposure,
        filled_value: float = 0.0,
    ) -> CapitalGuardDecision:
        """
        Validate after fill event and release reserved capital.
        """

        with self._lock:
            # Release reservation for filled portion
            if filled_value:
                self._reserved_global -= filled_value
                self._reserved_strategy -= filled_value
                self._reserved_symbol -= filled_value

                # Prevent negative reservation under race conditions
                self._reserved_global = max(self._reserved_global, 0.0)
                self._reserved_strategy = max(self._reserved_strategy, 0.0)
                self._reserved_symbol = max(self._reserved_symbol, 0.0)

            # Drift validation
            if updated_exposure.global_exposure > envelope.global_cap:
                return CapitalGuardDecision(
                    False, True, "GLOBAL_DRIFT_AFTER_FILL"
                )

            if updated_exposure.strategy_exposure > envelope.strategy_cap:
                return CapitalGuardDecision(
                    False, True, "STRATEGY_DRIFT_AFTER_FILL"
                )

            if updated_exposure.symbol_exposure > envelope.symbol_cap:
                return CapitalGuardDecision(
                    False, True, "SYMBOL_DRIFT_AFTER_FILL"
                )

        return CapitalGuardDecision(True, False, "POST_FILL_VALID")

    # =============================================================
    # RETRY VALIDATION
    # =============================================================

    def validate_retry(
        self,
        *,
        original_key: str,
        retry_key: str,
    ) -> CapitalGuardDecision:
        """
        Ensure idempotency key consistency.
        """

        if original_key != retry_key:
            return CapitalGuardDecision(
                False,
                True,
                "IDEMPOTENCY_KEY_MISMATCH",
            )

        return CapitalGuardDecision(True, False, "RETRY_VALID")

    # =============================================================
    # RECONCILIATION VALIDATION
    # =============================================================

    def validate_reconciliation(
        self,
        *,
        internal_position: float,
        broker_position: float,
    ) -> CapitalGuardDecision:
        """
        Detect broker vs internal ledger mismatch.
        """

        if internal_position != broker_position:
            return CapitalGuardDecision(
                False,
                True,
                "RECONCILIATION_MISMATCH",
            )

        return CapitalGuardDecision(True, False, "RECONCILIATION_VALID")

    # =============================================================
    # OPTIONAL: CANCEL RESERVATION (Order Cancel Path)
    # =============================================================

    def release_reservation(self, value: float) -> None:
        """
        Explicitly release reserved exposure (for cancelled orders).
        """

        with self._lock:
            self._reserved_global -= value
            self._reserved_strategy -= value
            self._reserved_symbol -= value

            self._reserved_global = max(self._reserved_global, 0.0)
            self._reserved_strategy = max(self._reserved_strategy, 0.0)
            self._reserved_symbol = max(self._reserved_symbol, 0.0)