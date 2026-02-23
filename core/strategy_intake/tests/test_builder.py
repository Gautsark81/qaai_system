from core.strategy_intake.builder import StrategyIntakeBuilder
from core.watchlist.models import WatchlistEntry


def test_intake_respects_min_confidence():
    watchlist = [
        WatchlistEntry("A", 1, 0.9, "screening", []),
        WatchlistEntry("B", 2, 0.3, "screening", []),
    ]

    batch = StrategyIntakeBuilder(
        min_confidence=0.5
    ).build(watchlist)

    assert len(batch.candidates) == 1
    assert batch.candidates[0].symbol == "A"


def test_intake_respects_max_symbols():
    watchlist = [
        WatchlistEntry("A", 1, 0.9, "screening", []),
        WatchlistEntry("B", 2, 0.8, "screening", []),
        WatchlistEntry("C", 3, 0.7, "screening", []),
    ]

    batch = StrategyIntakeBuilder(
        max_symbols=2
    ).build(watchlist)

    assert len(batch.candidates) == 2
