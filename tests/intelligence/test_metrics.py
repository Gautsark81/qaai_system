from modules.intelligence.metrics import StrategyMetricsExtractor
from modules.intelligence.ssr import TradeResult


def test_metrics_extraction():
    trades = [
        TradeResult(100, "FILLED"),
        TradeResult(-40, "FILLED"),
        TradeResult(10, "CANCELLED"),
    ]

    metrics = StrategyMetricsExtractor().extract(trades)

    assert metrics.total_trades == 2
    assert metrics.winning_trades == 1
    assert metrics.losing_trades == 1
    assert metrics.net_pnl == 60
