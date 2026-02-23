from modules.strategy_tournament.metrics import compute_symbol_metrics
from modules.strategy_tournament.result_schema import StrategyRunResult


def test_compute_symbol_metrics_empty():
    run = StrategyRunResult(
        strategy_id="s1",
        symbol="TEST",
        trades=[],
        total_pnl=0,
        max_drawdown=0,
        trade_count=0,
    )
    m = compute_symbol_metrics(run)
    assert m.trades == 0
    assert m.win_rate == 0.0
