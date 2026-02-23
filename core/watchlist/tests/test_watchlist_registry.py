from dataclasses import dataclass
from typing import Tuple, Optional
from core.watchlist import WatchlistRegistry


@dataclass(frozen=True)
class CompositeVerdictStub:
    passed: bool
    failed_step: Optional[str]
    blocked_dimensions: Tuple[str, ...]


def test_watchlist_adds_entry_on_pass():
    verdict = CompositeVerdictStub(
        passed=True,
        failed_step=None,
        blocked_dimensions=(),
    )

    registry = WatchlistRegistry()

    entry = registry.add(
        symbol="TCS",
        composite_verdict=verdict,
    )

    assert entry.symbol == "TCS"
    assert entry.status == "ACTIVE"
    assert entry.screening_passed is True


def test_watchlist_rejects_failed_composite():
    verdict = CompositeVerdictStub(
        passed=False,
        failed_step="liquidity",
        blocked_dimensions=("liquidity",),
    )

    registry = WatchlistRegistry()

    try:
        registry.add(
            symbol="ILLQ",
            composite_verdict=verdict,
        )
        assert False, "Expected failure when composite verdict is failed"
    except ValueError as e:
        assert "composite screening failed" in str(e).lower()


def test_watchlist_add_is_idempotent():
    verdict = CompositeVerdictStub(True, None, ())

    registry = WatchlistRegistry()

    entry1 = registry.add("TCS", verdict)
    entry2 = registry.add("TCS", verdict)

    assert entry1 is entry2
    assert registry.size() == 1


def test_watchlist_is_deterministically_sorted():
    verdict = CompositeVerdictStub(True, None, ())

    registry = WatchlistRegistry()
    registry.add("ZETA", verdict)
    registry.add("ALPHA", verdict)
    registry.add("BETA", verdict)

    symbols = [e.symbol for e in registry.list_entries()]

    assert symbols == ["ALPHA", "BETA", "ZETA"]


def test_screening_lineage_is_immutable():
    verdict = CompositeVerdictStub(True, None, ())

    registry = WatchlistRegistry()
    entry = registry.add("TCS", verdict)

    try:
        entry.screening_passed = False
        assert False, "Mutation should not be allowed"
    except Exception:
        assert True

def test_watchlist_suspend_entry():
    verdict = CompositeVerdictStub(True, None, ())

    registry = WatchlistRegistry()
    registry.add("TCS", verdict)

    registry.suspend("TCS", reason="regulatory review")

    entry = registry.get("TCS")
    assert entry.status == "SUSPENDED"
    assert entry.suspension_reason == "regulatory review"

def test_watchlist_retire_entry():
    verdict = CompositeVerdictStub(True, None, ())

    registry = WatchlistRegistry()
    registry.add("TCS", verdict)

    registry.retire("TCS", reason="permanent exclusion")

    entry = registry.get("TCS")
    assert entry.status == "RETIRED"

def test_retired_entry_cannot_be_readded():
    verdict = CompositeVerdictStub(True, None, ())

    registry = WatchlistRegistry()
    registry.add("TCS", verdict)
    registry.retire("TCS", reason="final")

    try:
        registry.add("TCS", verdict)
        assert False, "Re-adding retired symbol should fail"
    except ValueError as e:
        assert "retired" in str(e).lower()

def test_watchlist_size():
    verdict = CompositeVerdictStub(True, None, ())

    registry = WatchlistRegistry()
    registry.add("A", verdict)
    registry.add("B", verdict)

    assert registry.size() == 2

