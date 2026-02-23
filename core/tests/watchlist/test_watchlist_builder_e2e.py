from core.watchlist.builder import build_watchlist
from core.live_ops.screening import ScreeningResult


def test_builder_end_to_end():
    results = [
        ScreeningResult("A", True, [], 0.9),
        ScreeningResult("B", False, ["fail"], 0.8),
    ]

    snap = build_watchlist(results, max_symbols=10)
    assert len(snap.entries) == 1
    assert snap.entries[0].symbol == "A"
