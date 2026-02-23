from modules.portfolio.concentration import ConcentrationEngine


def test_concentration_detects_single_bet():
    weights = {"A": 1.0}
    c = ConcentrationEngine.effective_concentration(weights)
    assert c == 1.0


def test_concentration_diversified():
    weights = {"A": 0.5, "B": 0.5}
    c = ConcentrationEngine.effective_concentration(weights)
    assert c == 0.5
