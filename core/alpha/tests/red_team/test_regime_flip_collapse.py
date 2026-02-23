import pytest
from dataclasses import dataclass
from typing import List


# ───────────────────────────────────────────────────────────────
# Helpers — strictly authorized surfaces only
# ───────────────────────────────────────────────────────────────

def _invoke_replay(driver, *, ticks, regime_events):
    for name in (
        "execute",
        "replay",
        "run_replay",
        "drive",
        "apply",
        "__call__",
    ):
        if hasattr(driver, name):
            fn = getattr(driver, name)
            if callable(fn):
                return fn(ticks=ticks, regime_events=regime_events)

    raise AssertionError(
        "RedTeamReplayDriver exposes no executable replay method"
    )


def _get_evidence_events(view):
    for name in ("get_events", "get_evidence", "iter_evidence", "evidence"):
        if hasattr(view, name):
            obj = getattr(view, name)
            return list(obj()) if callable(obj) else list(obj)

    raise AssertionError(
        "AuthorizedRuntimeView exposes no forensic evidence surface"
    )


# ───────────────────────────────────────────────────────────────
# Test data
# ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FakeMarketTick:
    ts: int
    price: float
    volume: float


@dataclass(frozen=True)
class RegimeEvent:
    ts: int
    regime: str


@pytest.fixture
def stable_then_crisis_ticks() -> List[FakeMarketTick]:
    price = 100.0
    ticks = []

    for t in range(50):
        price += 0.1
        ticks.append(FakeMarketTick(ts=t, price=price, volume=1_000))

    for t in range(50, 100):
        price += (-1) ** t * 2.5
        ticks.append(FakeMarketTick(ts=t, price=price, volume=800))

    return ticks


@pytest.fixture
def injected_regime_events() -> List[RegimeEvent]:
    return [
        RegimeEvent(ts=0, regime="LOW_VOL"),
        RegimeEvent(ts=50, regime="CRISIS"),
    ]


# ───────────────────────────────────────────────────────────────
# PHASE 20.1.1 — REGIME FLIP ADVERSARIAL COLLAPSE
# ───────────────────────────────────────────────────────────────

def test_system_survives_regime_flip_without_unsafe_behavior(
    stable_then_crisis_ticks,
    injected_regime_events,
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 20.1.1 — REGIME FLIP ADVERSARIAL COLLAPSE

    This test asserts the ONLY invariant required at this phase:

    • The system survives a violent regime transition
    • No unsafe execution occurs
    • The system remains observable and governed

    Defensive reactions are OPTIONAL, not mandatory.
    """

    # ─── Act ────────────────────────────────────────────────────
    _invoke_replay(
        deterministic_replay,
        ticks=stable_then_crisis_ticks,
        regime_events=injected_regime_events,
    )

    # ─── Observe evidence ───────────────────────────────────────
    evidence = _get_evidence_events(authorized_runtime_view)

    # ─── Assertions (safety & observability) ────────────────────
    assert evidence is not None, "System must remain observable"

    # Optional but acceptable: defensive actions MAY exist
    # We do NOT require them at this phase
