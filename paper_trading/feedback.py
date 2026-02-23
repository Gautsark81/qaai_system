from __future__ import annotations


class FeedbackLoop:
    """
    Maintains a bounded score per symbol in [0, 1].
    Positive PnL nudges score up; negative PnL nudges down.
    """

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.scores: dict[str, float] = {}

    def get(self, symbol: str) -> float:
        return self.scores.get(symbol, 0.5)

    def update_after_trade(self, symbol: str, realized_pnl: float, notional: float):
        if notional <= 0:
            return self.get(symbol)
        # normalized outcome in [-1, 1]
        outcome = max(-1.0, min(1.0, realized_pnl / max(notional, 1e-9)))
        score = self.get(symbol)
        score = score + self.alpha * outcome
        score = max(0.0, min(1.0, score))
        self.scores[symbol] = score
        return score
