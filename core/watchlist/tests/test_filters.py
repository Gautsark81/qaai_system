from core.watchlist.filters import filter_passed, filter_min_score
from core.live_ops.screening import ScreeningResult


def _sr(symbol, passed, score):
    return ScreeningResult(
        symbol=symbol,
        passed=passed,
        reasons=[],
        score=score,
    )


def test_filter_passed():
    data = [
        _sr("A", True, 0.9),
        _sr("B", False, 0.8),
    ]

    out = filter_passed(data)
    assert len(out) == 1
    assert out[0].symbol == "A"


def test_filter_min_score():
    data = [
        _sr("A", True, 0.7),
        _sr("B", True, 0.4),
    ]

    out = filter_min_score(data, min_score=0.6)
    assert len(out) == 1
