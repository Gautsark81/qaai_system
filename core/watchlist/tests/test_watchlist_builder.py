from core.watchlist.watchlist_builder import WatchlistBuilder
from core.live_ops.screening import ScreeningResult


def _r(symbol, score, passed=True):
    return ScreeningResult(
        symbol=symbol,
        score=score,
        passed=passed,
        reasons=["rule_ok"],
    )


def test_watchlist_filters_and_ranks():
    results = [
        _r("A", 0.9),
        _r("B", 0.7),
        _r("C", 0.4),  # below threshold
    ]

    wl = WatchlistBuilder().build(results)

    assert wl.total == 2
    assert wl.entries[0].symbol == "A"
    assert wl.entries[1].symbol == "B"


def test_watchlist_is_deterministic():
    results = [
        _r("X", 0.8),
        _r("Y", 0.8),
    ]

    w1 = WatchlistBuilder().build(results)
    w2 = WatchlistBuilder().build(results)

    assert w1 == w2
