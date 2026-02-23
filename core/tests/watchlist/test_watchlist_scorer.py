from core.watchlist.scorer import score_screening_result
from core.live_ops.screening import ScreeningResult


def test_score_penalty_applied():
    r = ScreeningResult("A", True, ["x"], 0.8)
    assert score_screening_result(r) < 0.8
