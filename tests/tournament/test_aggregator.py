from modules.tournament.aggregator import TournamentResultAggregator
from modules.intelligence.ssr import TradeResult


def test_aggregate_ssr_and_metrics():
    results = {
        "A": [
            TradeResult(100, "FILLED"),
            TradeResult(-50, "FILLED"),
        ],
        "B": [
            TradeResult(40, "FILLED"),
        ],
    }

    agg = TournamentResultAggregator().aggregate(results)

    assert agg["ssr"] == 0.6667
    assert agg["metrics"].total_trades == 3
    assert agg["metrics"].net_pnl == 90
