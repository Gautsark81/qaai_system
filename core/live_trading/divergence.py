class DivergenceAnalyzer:
    """
    Computes execution divergence between paper and live.
    """

    def compute_slippage(self, paper_price: float, live_price: float) -> float:
        return live_price - paper_price

    def divergence_score(self, samples) -> float:
        if not samples:
            return 0.0

        total = 0.0
        for s in samples:
            total += abs(s.live_price - s.paper_price)

        return total / len(samples)
