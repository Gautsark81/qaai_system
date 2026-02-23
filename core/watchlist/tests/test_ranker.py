from core.watchlist.ranker import rank_by_score
from core.live_ops.screening import ScreeningResult


def test_rank_is_deterministic():
    data = [
        ScreeningResult("B", True, [], 0.7),
        ScreeningResult("A", True, [], 0.7),
        ScreeningResult("C", True, [], 0.9),
    ]

    ranked = rank_by_score(data)

    assert ranked[0].symbol == "C"
    assert ranked[1].symbol == "A"
    assert ranked[2].symbol == "B"
