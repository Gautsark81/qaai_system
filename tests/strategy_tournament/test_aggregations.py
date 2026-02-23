from modules.strategy_tournament.aggregations import aggregate_strategy_metrics
from modules.strategy_tournament.metrics import SymbolMetrics


def test_aggregate_strategy_metrics():
    metrics = [
        SymbolMetrics("A", 10, 6, 4, 0.6, 100, 5),
        SymbolMetrics("B", 5, 3, 2, 0.6, 50, 3),
    ]

    agg = aggregate_strategy_metrics("s1", metrics)
    assert agg.total_trades == 15
    assert agg.symbols_traded == 2
