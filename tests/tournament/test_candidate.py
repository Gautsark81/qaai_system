from modules.tournament.candidate import StrategyCandidate


def test_candidate_immutable():
    c = StrategyCandidate("s1", {"a": 1}, generation=0)
    assert c.strategy_id == "s1"
