# tests/watchlist/test_watchlist_coordinator.py
from screening.results import ScreeningResult
from watchlist.service import WatchlistService
from watchlist.coordinator import WatchlistCoordinator, CoordinationRule


def test_coordinator_apply_rules_and_priority(tmp_path):
    base_dir = tmp_path / "watchlists"
    wl = WatchlistService(base_dir=str(base_dir))
    coord = WatchlistCoordinator(wl)

    # Fake screen results with scores and some overlap
    mom_results = [
        ScreeningResult(symbol="A", score=3.0),
        ScreeningResult(symbol="B", score=2.0),
        ScreeningResult(symbol="C", score=1.0),
    ]
    meanrev_results = [
        ScreeningResult(symbol="C", score=5.0),
        ScreeningResult(symbol="D", score=4.0),
    ]

    results_by_screen = {
        "MOMENTUM_LONG": mom_results,
        "MEANREVERT_LONG": meanrev_results,
    }

    rules = [
        CoordinationRule(
            source_screen="MOMENTUM_LONG",
            target_watchlist="LONG_CORE",
            mode="replace",
            max_symbols=2,   # A,B
        ),
        CoordinationRule(
            source_screen="MEANREVERT_LONG",
            target_watchlist="LONG_SECONDARY",
            mode="replace",
        ),
    ]

    coord.apply_rules(results_by_screen, rules)

    long_core = wl.get("LONG_CORE")
    long_sec = wl.get("LONG_SECONDARY")

    assert long_core == ["A", "B"]
    assert set(long_sec) == {"C", "D"}

    # Now enforce priority: LONG_CORE > LONG_SECONDARY
    coord.enforce_priority(["LONG_CORE", "LONG_SECONDARY"])

    long_core = wl.get("LONG_CORE")
    long_sec = wl.get("LONG_SECONDARY")

    # LONG_CORE stays the same
    assert long_core == ["A", "B"]
    # C/D still okay but if A/B leaked into SECONDARY they'd be removed
    assert set(long_sec).issubset({"C", "D"})
    assert not (set(long_core) & set(long_sec))
