import pytest
from dataclasses import dataclass
from typing import List, Tuple


# ───────────────────────────────────────────────────────────────
# Helpers — authorized surfaces only
# ───────────────────────────────────────────────────────────────

def _invoke(driver, *, ticks):
    for name in ("execute", "replay", "run", "__call__"):
        if hasattr(driver, name):
            fn = getattr(driver, name)
            if callable(fn):
                return fn(ticks=ticks, regime_events=[])

    raise AssertionError("No executable replay entrypoint found")


def _get_events(view):
    for name in ("get_events", "get_evidence", "iter_evidence", "evidence"):
        if hasattr(view, name):
            obj = getattr(view, name)
            return list(obj()) if callable(obj) else list(obj)

    return []


def _fingerprint(events) -> Tuple:
    """
    Generate a deterministic fingerprint from observable evidence.
    Order-independent, payload-stable.
    """
    return tuple(
        sorted(
            (e.event_type, tuple(sorted(e.payload.items())))
            for e in events
        )
    )


# ───────────────────────────────────────────────────────────────
# Test data — identical reality, different clocks
# ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FakeMarketTick:
    ts: int
    price: float
    volume: float


@pytest.fixture
def identical_market_realities() -> Tuple[List[FakeMarketTick], List[FakeMarketTick]]:
    """
    Same market evolution, different timestamp alignment.
    """
    price = 100.0
    ticks_a, ticks_b = [], []

    for i in range(60):
        price += 0.4
        ticks_a.append(FakeMarketTick(ts=i, price=price, volume=1_000))
        ticks_b.append(FakeMarketTick(ts=i * 5, price=price, volume=1_000))

    return ticks_a, ticks_b


# ───────────────────────────────────────────────────────────────
# PHASE 20.4 — REPLAY DRIFT ATTACK
# ───────────────────────────────────────────────────────────────

def test_replay_is_time_alignment_invariant(
    identical_market_realities,
    system_runtime,
    authorized_runtime_view,
):
    """
    PHASE 20.4 — REPLAY DRIFT ATTACK

    Same market reality.
    Different timestamps.
    Identical forensic outcomes.

    Replay must not fork reality.
    """

    ticks_a, ticks_b = identical_market_realities

    from core.conftest import RedTeamReplayDriver

    # ─── Replay A ───────────────────────────────────────────────
    driver_a = RedTeamReplayDriver(system_runtime, authorized_runtime_view)
    run_id_a = driver_a._run_id

    _invoke(driver_a, ticks=ticks_a)

    events_a = [
        e for e in _get_events(authorized_runtime_view)
        if e.run_id == run_id_a
    ]
    fingerprint_a = _fingerprint(events_a)

    # ─── Replay B ───────────────────────────────────────────────
    driver_b = RedTeamReplayDriver(system_runtime, authorized_runtime_view)
    run_id_b = driver_b._run_id

    _invoke(driver_b, ticks=ticks_b)

    events_b = [
        e for e in _get_events(authorized_runtime_view)
        if e.run_id == run_id_b
    ]
    fingerprint_b = _fingerprint(events_b)

    # ─── Assertion — absolute determinism ───────────────────────
    assert fingerprint_a == fingerprint_b, (
        "Replay drift detected: identical market reality "
        "produced divergent forensic outcomes"
    )
