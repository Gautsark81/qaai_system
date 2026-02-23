from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.market_clock.nse_clock import NSEMarketClock
from core.safety.kill_switch import GlobalKillSwitch, KillSwitchEvent


# ==========================================================
# Exceptions
# ==========================================================

class TimeDriftViolation(RuntimeError):
    """
    Raised when broker-reported time drifts beyond safe threshold
    relative to NSE market time.
    """


# ==========================================================
# Broker Time Drift Guard
# ==========================================================

@dataclass(frozen=True)
class BrokerTimeDriftGuard:
    """
    Hard safety guard that enforces strict alignment between
    broker server time and NSE market time.

    DESIGN GUARANTEES:
    - Deterministic
    - Stateless
    - Latching via GlobalKillSwitch
    - No env overrides
    - No auto reset
    """

    market_clock: NSEMarketClock
    kill_switch: GlobalKillSwitch
    max_drift_seconds: int = 2

    # ------------------------------------------------------
    # Core Check
    # ------------------------------------------------------
    def assert_safe(self, *, broker_time: datetime) -> None:
        """
        Validate broker time against NSE market time.

        If drift exceeds allowed threshold:
        - Engage GlobalKillSwitch
        - Raise TimeDriftViolation
        """

        # If already killed → hard stop
        if self.kill_switch.is_active:
            raise RuntimeError("GlobalKillSwitch already engaged")

        nse_time = self.market_clock.now_utc

        # Absolute drift in seconds
        drift_seconds = abs((broker_time - nse_time).total_seconds())

        if drift_seconds <= self.max_drift_seconds:
            return  # SAFE

        # ----------------------------------------------
        # VIOLATION → HARD HALT
        # ----------------------------------------------
        reason = (
            f"Broker time drift detected: "
            f"{drift_seconds:.2f}s "
            f"(allowed={self.max_drift_seconds}s)"
        )

        self.kill_switch.engage(
            reason=reason,
            triggered_by="broker_time_drift_guard",
        )

        raise TimeDriftViolation(reason)
