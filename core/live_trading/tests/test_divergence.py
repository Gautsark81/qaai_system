from core.live_trading.divergence import DivergenceAnalyzer
from core.live_trading.telemetry import ExecutionSample


def test_divergence_score():
    samples = [
        ExecutionSample("N", 100.0, 101.0, 0),
        ExecutionSample("N", 100.0, 99.5, 0),
    ]

    d = DivergenceAnalyzer()
    score = d.divergence_score(samples)

    assert score == (1.0 + 0.5) / 2
