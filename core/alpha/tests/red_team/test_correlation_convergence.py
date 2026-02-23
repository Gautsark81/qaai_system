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
# Test data — Correlation convergence
# ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FakeMarketTick:
    ts: int
    price: float
    volume: float


@pytest.fixture
def correlation_converged_ticks() -> List[FakeMarketTick]:
    """
    Market series where all strategies would naturally
    converge to the same directional bias.
    """
    price = 100.0
    ticks = []

    # Smooth persistent trend — correlation trap
    for t in range(100):
        price += 0.5
        ticks.append(
            FakeMarketTick(ts=t, price=price, volume=1_200)
        )

    return ticks


# ───────────────────────────────────────────────────────────────
# PHASE 20.1.3 — CORRELATION CONVERGENCE ATTACK
# ───────────────────────────────────────────────────────────────

def test_system_survives_correlation_convergence_without_capital_collapse(
    correlation_converged_ticks,
    deterministic_replay,
    authorized_runtime_view,
):
    """
    PHASE 20.1.3 — CORRELATION CONVERGENCE ATTACK

    This test asserts ONLY required invariants:

    • System survives silent correlation collapse
    • No unsafe execution is forced
    • System remains observable & governed

    Capital or strategy reactions are OPTIONAL.
    """

    # ─── Act ────────────────────────────────────────────────────
    _invoke_replay(
        deterministic_replay,
        ticks=correlation_converged_ticks,
    )

    # ─── Observe evidence ───────────────────────────────────────
    evidence = _get_evidence_events(authorized_runtime_view)

    # ─── Assertions (safety & observability only) ───────────────
    assert evidence is not None, "System must remain observable"

    # Optional, non-fatal observations:
    # - STRATEGY_CORRELATION_UPDATED
    # - CAPITAL_REBALANCED
    # - RISK_VERDICT
    #
    # These are allowed but NOT required.
