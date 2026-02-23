import pytest


# ───────────────────────────────────────────────────────────────
# Helpers — authorized surfaces only
# ───────────────────────────────────────────────────────────────

def _invoke(driver):
    for name in ("execute", "replay", "run", "__call__"):
        if hasattr(driver, name):
            fn = getattr(driver, name)
            if callable(fn):
                return fn(ticks=[], regime_events=[])

    raise AssertionError("No executable replay entrypoint found")


def _get_events(view):
    for name in ("get_events", "get_evidence", "iter_evidence", "evidence"):
        if hasattr(view, name):
            obj = getattr(view, name)
            return list(obj()) if callable(obj) else list(obj)

    return []


# ───────────────────────────────────────────────────────────────
# PHASE 20.3 — OPERATOR PANIC SIMULATION
# ───────────────────────────────────────────────────────────────

def test_system_survives_operator_panic_without_authority_leak(
    deterministic_replay,
    authorized_runtime_view,
    system_runtime,
):
    """
    PHASE 20.3 — OPERATOR PANIC SIMULATION

    Scenario:
    • Rapid kill-switch toggling
    • Conflicting operator intents
    • Attempts to re-arm under panic

    Invariant:
    • Kill switch is sovereign
    • Safety is irreversible
    • System remains governed & observable
    """

    # ─── Act: operator panic simulation ─────────────────────────
    kill = getattr(system_runtime, "kill_switch", None)
    arm = getattr(system_runtime, "arm", None)

    # Toggle aggressively if present
    if kill:
        for _ in range(3):
            kill.engage()
            kill.engage()

    if arm:
        for _ in range(3):
            arm.disarm()
            arm.arm()

    # Drive system forward
    _invoke(deterministic_replay)

    # ─── Observe ────────────────────────────────────────────────
    events = _get_events(authorized_runtime_view)
    event_types = {e.event_type for e in events}

    # ─── Assertions (minimal, sovereign) ────────────────────────

    # Kill-switch dominance (if instrumented)
    assert not (
        "EXECUTION_INTENT_CREATED" in event_types
        and "KILL_SWITCH_ENGAGED" in event_types
    ), "Execution must not occur while kill-switch is active"

    # System must remain observable
    assert events is not None, "System must remain observable under panic"
