# modules/strategy_tournament/scorer.py

from modules.strategy_tournament.contribution import Contribution


def score_contribution(c: Contribution) -> float:
    """
    Linear, explainable contribution score.
    Weights are fixed & governed.
    """
    return (
        2.0 * c.delta_ssr
        + 1.5 * c.delta_drawdown
        + 0.5 * c.delta_symbols
    )
