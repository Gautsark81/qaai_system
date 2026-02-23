from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional, Tuple

from core.telemetry.emitter import TelemetryEmitter
from core.telemetry.event import TelemetryEvent
from core.telemetry.types import TelemetryCategory, TelemetrySeverity

from .scopes import KillScope


# =====================================================
# PHASE 19.1 — GLOBAL KILL SWITCH (TEST-LOCKED)
# =====================================================


class KillSwitchState(str, Enum):
    DISENGAGED = "DISENGAGED"
    ENGAGED = "ENGAGED"


@dataclass(frozen=True)
class KillSwitchEvent:
    state: KillSwitchState
    reason: str
    triggered_by: str
    timestamp: datetime


class GlobalKillSwitch:
    """
    Global, latched, auditable kill switch.

    Guarantees:
    - Latched (single engage)
    - Operator-only reset
    - Deterministic reads
    - Immutable audit events
    """

    def __init__(self) -> None:
        self._state: KillSwitchState = KillSwitchState.DISENGAGED
        self._engaged_event: Optional[KillSwitchEvent] = None

    # --------------------
    # Read-only properties
    # --------------------

    @property
    def state(self) -> KillSwitchState:
        return self._state

    @property
    def is_active(self) -> bool:
        return self._state == KillSwitchState.ENGAGED

    # --------------------
    # Transitions
    # --------------------

    def engage(self, *, reason: str, triggered_by: str) -> KillSwitchEvent:
        if self._state == KillSwitchState.ENGAGED:
            raise RuntimeError("Kill switch already engaged (latched)")

        event = KillSwitchEvent(
            state=KillSwitchState.ENGAGED,
            reason=reason,
            triggered_by=triggered_by,
            timestamp=datetime.now(tz=timezone.utc),
        )

        self._state = KillSwitchState.ENGAGED
        self._engaged_event = event

        return event

    def reset(self, *, triggered_by: str) -> KillSwitchEvent:
        if self._state != KillSwitchState.ENGAGED:
            raise RuntimeError("Kill switch is not engaged")

        if triggered_by != "operator":
            raise RuntimeError("Kill switch reset requires explicit operator action")

        event = KillSwitchEvent(
            state=KillSwitchState.DISENGAGED,
            reason="Operator reset",
            triggered_by=triggered_by,
            timestamp=datetime.now(tz=timezone.utc),
        )

        self._state = KillSwitchState.DISENGAGED
        self._engaged_event = None

        return event


# =====================================================
# EXISTING KILLSWITCH (GOVERNANCE + EXECUTION)
# PRESERVED — NO SEMANTIC CHANGES
# =====================================================


class KillSwitch:
    """
    Deterministic, scoped, idempotent kill switch.

    Supports:
    - Scoped governance kills (GLOBAL / STRATEGY / SYMBOL)
    - Execution-level global kill (persistent across restart)
    """

    def __init__(
        self,
        telemetry: Optional[TelemetryEmitter] = None,
        *,
        scope: Optional[str] = None,
        base_path: Optional[str] = None,
    ):
        self._telemetry = telemetry
        self._tripped: Dict[Tuple[KillScope, Optional[str]], str] = {}
        self._lock = threading.RLock()

        self._exec_scope = scope
        if scope is not None:
            root = base_path or os.getenv("QA_STATE_PATH", "data")
            os.makedirs(root, exist_ok=True)
            self._state_file = os.path.join(root, f"kill_switch_{scope}.flag")
        else:
            self._state_file = None

    # --------------------
    # GOVERNANCE API
    # --------------------

    def trip(
        self,
        scope: KillScope,
        *,
        key: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        k = (scope, key)

        if k in self._tripped:
            return

        normalized_reason = reason or "unspecified"
        self._tripped[k] = normalized_reason

        self._emit(scope=scope, key=key, reason=normalized_reason)

        if scope == KillScope.GLOBAL:
            self.arm(reason=normalized_reason)

    def is_tripped(self, scope: KillScope, key: Optional[str] = None) -> bool:
        return (scope, key) in self._tripped

    def reason(self, scope: KillScope, key: Optional[str] = None) -> Optional[str]:
        return self._tripped.get((scope, key))

    def assert_can_trade(self) -> None:
        if self.is_tripped(KillScope.GLOBAL):
            raise RuntimeError("Trading halted by global kill switch")

    # --------------------
    # EXECUTION API
    # --------------------

    def is_armed(self) -> bool:
        if not self._state_file:
            return False
        return os.path.exists(self._state_file)

    def arm(self, reason: Optional[str] = None) -> None:
        if not self._state_file:
            return

        with self._lock:
            if not self.is_armed():
                with open(self._state_file, "w") as f:
                    f.write(reason or "armed")

    def disarm(self) -> None:
        if not self._state_file:
            return

        with self._lock:
            try:
                os.remove(self._state_file)
            except FileNotFoundError:
                pass

    def assert_not_armed(self) -> None:
        if self.is_armed():
            raise RuntimeError(
                f"KillSwitch[{self._exec_scope}] is ARMED — execution blocked"
            )

    # --------------------
    # INTERNAL
    # --------------------

    def _emit(self, scope: KillScope, key: Optional[str], reason: str) -> None:
        if not self._telemetry:
            return

        event = TelemetryEvent.create(
            category=TelemetryCategory.ERROR,
            severity=TelemetrySeverity.CRITICAL,
            run_id="unknown",
            payload={
                "kill_scope": scope.value,
                "key": key,
                "reason": reason,
            },
        )

        self._telemetry.emit(event)
