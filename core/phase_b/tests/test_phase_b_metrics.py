from core.phase_b.metrics import StrategyMetrics
from core.phase_b.ssr import compute_ssr


def test_metrics_win_rate():
    m = StrategyMetrics(
        dna="abc",
        trades=10,
        wins=6,
        losses=4,
        pnl=120.0,
    )

    assert m.win_rate == 0.6


def test_ssr_computation():
    m = StrategyMetrics(
        dna="abc",
        trades=9,
        wins=6,
        losses=3,
        pnl=90.0,
    )

    ssr = compute_ssr(m)
    assert ssr is not None
    assert ssr > 0
