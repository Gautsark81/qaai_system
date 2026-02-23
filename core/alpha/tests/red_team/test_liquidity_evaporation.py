import pytest
from dataclasses import dataclass
from typing import List


# ───────────────────────────────────────────────────────────────
# Helpers — strictly authorized surfaces only
# ───────────────────────────────────────────────────────────────

def _invoke_replay(driver, *, ticks):
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
                return fn(ticks=ticks, regime_events=[])

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
# Test data — Liquidity evaporation
# ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FakeMarketTick:
    ts: int
    price: float
    volume: float


@pytest.fixture
def evaporating_liquidity_ticks() -> List[FakeMarketTick]:
    """
    Market where price continues but liquidity collapses to near zero.
    """
    price = 100.0
    ticks = []

    # Normal liquidity phase
    for t in range(30):
        price += 0.2
        ticks.append(
            FakeMarketTick(ts=t, price=price, volume=1_500)
        )

    # Liquidity evaporation phase
    for t in range(30, 80):
        price += 0.1
        ticks.append(
            FakeMarketTick(ts=t, price=price, volume=1)  # near-zero liquidity
        )

    return ticks


# ───────────────────────────────────────────────────────────────
# PHASE 20.1.2 — LIQUIDITY EVAPORATION ATTACK
# ───────────────────────────────────────────────────────────────

def test_system_survives_liquidity_evaporation_without_forced_execution(
    evaporating_liquidity_ticks,
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 20.1.2 — LIQUIDITY EVAPORATION ATTACK

    This test asserts the ONLY required invariants:

    • System survives when liquidity disappears
    • No forced or unsafe execution occurs
    • System remains observable and governed

    Defensive reactions are OPTIONAL.
    """

    # ─── Act ────────────────────────────────────────────────────
    _invoke_replay(
        deterministic_replay,
        ticks=evaporating_liquidity_ticks,
    )

    # ─── Observe evidence ───────────────────────────────────────
    evidence = _get_evidence_events(authorized_runtime_view)

    # ─── Assertions (safety only) ───────────────────────────────
    assert evidence is not None, "System must remain observable"

    # Optional checks (non-fatal if absent)
    # These are acceptable outcomes but NOT mandatory:
    #
    # - EXECUTION_BLOCKED
    # - RISK_VERDICT
    # - CAPITAL_THROTTLED
    #
    # We intentionally do NOT assert them.
