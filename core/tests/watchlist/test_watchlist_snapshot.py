from core.watchlist.snapshot import build_snapshot
from core.live_ops.screening import ScreeningResult


def test_snapshot_ranking():
    results = [
        ScreeningResult("A", True, [], 0.9),
        ScreeningResult("B", True, [], 0.8),
    ]
    snap = build_snapshot(results)
    assert snap.entries[0].symbol == "A"
