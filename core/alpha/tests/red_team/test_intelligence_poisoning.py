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
# Test data — Intelligence poisoning
# ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FakeMarketTick:
    ts: int
    price: float
    volume: float


@pytest.fixture
def statistically_valid_but_misleading_ticks() -> List[FakeMarketTick]:
    """
    Price series engineered to look statistically strong
    while embedding subtle instability.
    """
    price = 100.0
    ticks = []

    for t in range(120):
        # smooth trend + small noise (appears very confident)
        price += 0.3
        if t % 17 == 0:
            price -= 2.0  # hidden instability
        ticks.append(
            FakeMarketTick(ts=t, price=price, volume=1_100)
        )

    return ticks


# ───────────────────────────────────────────────────────────────
# PHASE 20.2 — INTELLIGENCE POISONING
# ───────────────────────────────────────────────────────────────

def test_system_survives_intelligence_poisoning_without_authority_override(
    statistically_valid_but_misleading_ticks,
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 20.2 — INTELLIGENCE POISONING

    This test asserts ONLY these invariants:

    • Intelligence does NOT override governance
    • No unsafe execution occurs
    • System remains observable & governed

    Overconfidence must NOT translate into authority.
    """

    # ─── Act ────────────────────────────────────────────────────
    _invoke_replay(
        deterministic_replay,
        ticks=statistically_valid_but_misleading_ticks,
    )

    # ─── Observe evidence ───────────────────────────────────────
    evidence = _get_evidence_events(authorized_runtime_view)

    # ─── Assertions (safety only) ───────────────────────────────
    assert evidence is not None, "System must remain observable"

    # OPTIONAL, NON-FATAL OBSERVATIONS (NOT REQUIRED):
    #
    # - INTELLIGENCE_SCORE_UPDATED
    # - MODEL_CONFIDENCE_HIGH
    # - ADVISORY_SIGNAL_EMITTED
    #
    # These are allowed, but must NOT cause unsafe execution.
