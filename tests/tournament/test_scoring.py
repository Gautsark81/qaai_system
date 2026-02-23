from qaai_system.tournament.scoring import score_strategy


def test_scoring_positive(dummy_snapshot):
    score = score_strategy(dummy_snapshot)
    assert score > 0
