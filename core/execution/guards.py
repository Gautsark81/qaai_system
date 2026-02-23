# core/execution/guards.py
from __future__ import annotations

import inspect
import logging
from typing import Callable, Optional

from core.telemetry.event import TelemetryEvent
from core.telemetry.types import TelemetryCategory, TelemetrySeverity

# Note: we intentionally do a lazy provider registration so system bootstrap can
# register the single, authoritative KillSwitch instance used across the process.
_kill_switch_provider: Optional[Callable[[], object]] = None

logger = logging.getLogger(__name__)


def register_kill_switch(provider: Callable[[], object]) -> None:
    """
    Register a callable that returns the authoritative KillSwitch instance.

    Example at bootstrap:
        register_kill_switch(lambda: my_global_kill_switch)
    """
    global _kill_switch_provider
    _kill_switch_provider = provider


def _get_kill_switch():
    if _kill_switch_provider is None:
        raise RuntimeError(
            "KillSwitch provider not registered. Call register_kill_switch(...) at boot."
        )
    return _kill_switch_provider()


def assert_execution_allowed(*, callsite: Optional[str] = None) -> None:
    """
    Canonical guard that must be called at EVERY broker-facing edge.

    Raises RuntimeError if execution is blocked by the kill switch (execution-layer).
    """
    ks = _get_kill_switch()

    # Prefer explicit API: kill switch exposes assert_not_armed() for execution gating
    # and is_tripped(...) for governance-level gating.
    try:
        # 1) Execution-level hard gate (file-latched armed state)
        if hasattr(ks, "is_armed") and ks.is_armed():
            raise RuntimeError("Execution blocked: KillSwitch is ARMED (execution layer)")

        # 2) Governance-level global trip
        if hasattr(ks, "is_tripped") and ks.is_tripped(getattr(ks, "GLOBAL", None) or None):
            raise RuntimeError("Execution blocked: KillSwitch is tripped (governance)")

    except RuntimeError:
        _emit_blocked_telemetry(callsite=callsite or _caller(), ks=ks)
        raise

def is_execution_allowed() -> bool:
    try:
        assert_execution_allowed()
        return True
    except RuntimeError:
        return False


def _caller() -> str:
    # helper to find the caller for telemetry
    stack = inspect.stack()
    if len(stack) < 3:
        return "<unknown>"
    frame = stack[2]
    return f"{frame.filename}:{frame.lineno}"


def _emit_blocked_telemetry(callsite: str, ks) -> None:
    # non-fatal if telemetry subsystem missing
    try:
        emitter = None
        if hasattr(ks, "telemetry"):
            emitter = getattr(ks, "telemetry")
        elif hasattr(ks, "_telemetry"):
            emitter = getattr(ks, "_telemetry")

        payload = {
            "reason": "kill_switch_block",
            "callsite": callsite,
            "kill_armed": getattr(ks, "is_armed", lambda: None)(),
        }

        if emitter is not None:
            event = TelemetryEvent.create(
                category=TelemetryCategory.ERROR,
                severity=TelemetrySeverity.CRITICAL,
                run_id="unknown",
                payload=payload,
            )
            emitter.emit(event)
        else:
            logger.critical("Execution blocked by kill switch: %s", payload)
    except Exception:
        logger.exception("Failed emitting kill-switch telemetry")
