# modules/operator_dashboard/adapters/system_health_adapter.py

from dataclasses import dataclass
from typing import Any, Dict


# ============================
# Snapshot Contract
# ============================

@dataclass(frozen=True)
class SystemHealthSnapshot:
    """
    Immutable, dashboard-safe system health snapshot.

    This object is:
    - Read-only
    - Deterministic
    - Safe when core runtime is not initialized
    """

    mode: str
    status: str
    kill_switch: bool
    timestamp: Any


# ============================
# Adapter
# ============================

class SystemHealthAdapter:
    """
    Read-only adapter.

    IMPORTANT:
    - Must NOT assume global registries exist
    - Must NEVER mutate core state
    - Must ALWAYS return a deterministic structure
    """

    def snapshot(self) -> SystemHealthSnapshot:
        try:
            # Lazy import to avoid hard dependency during tests
            from core.state.system_state import SystemState

            # SystemState exposes a safe current() accessor
            system_state: SystemState = SystemState.current()

            return SystemHealthSnapshot(
                mode=system_state.mode,
                status=system_state.status,
                kill_switch=system_state.kill_switch_engaged,
                timestamp=system_state.timestamp,
            )

        except Exception:
            # ✅ Deterministic fallback (cold start / tests)
            return SystemHealthSnapshot(
                mode="UNKNOWN",
                status="UNKNOWN",
                kill_switch=False,
                timestamp=None,
            )


# ============================
# Public Adapter Entrypoint
# ============================

def get_system_health_snapshot() -> SystemHealthSnapshot:
    """
    Canonical dashboard adapter entrypoint.

    SnapshotRegistry imports ONLY this function.
    """
    return SystemHealthAdapter().snapshot()
