from core.watchlist.builder import build_watchlist
from core.live_ops.screening import ScreeningResult
from core.live_ops.watchlist import WatchlistEntry


def test_build_watchlist_outputs_contracts():
    results = [
        ScreeningResult("A", True, [], 0.8),
        ScreeningResult("B", True, [], 0.9),
        ScreeningResult("C", False, [], 0.95),
    ]

    watchlist = build_watchlist(results)

    assert len(watchlist) == 2

    for w in watchlist:
        assert isinstance(w, WatchlistEntry)
        assert 0.0 <= w.confidence <= 1.0


def test_build_watchlist_respects_max_symbols():
    results = [
        ScreeningResult(f"S{i}", True, [], 0.9) for i in range(20)
    ]

    watchlist = build_watchlist(results, max_symbols=5)
    assert len(watchlist) == 5
