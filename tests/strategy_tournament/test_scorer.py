from modules.strategy_tournament.scorer import score_contribution
from modules.strategy_tournament.contribution import Contribution


def test_score_positive():
    c = Contribution(
        delta_ssr=0.1,
        delta_drawdown=1.0,
        delta_symbols=2,
    )
    assert score_contribution(c) > 0
