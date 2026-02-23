from modules.strategy_health.evaluator import StrategyHealthEvaluator


def test_healthy_strategy_scores_high():
    evaluator = StrategyHealthEvaluator()
    trades = [10, 12, -5, 8, 9, 11] * 10
    equity = list(range(len(trades)))

    result = evaluator.evaluate(
        strategy_id="s1",
        trade_pnls=trades,
        equity_curve=equity,
        window=50,
    )

    assert result.health_score > 0.7
    assert "DRAWDOWN_RISK" not in result.flags


def test_strategy_with_large_drawdown_flags_risk():
    evaluator = StrategyHealthEvaluator()
    trades = [10, 10, -50, -40, -30]
    equity = [100, 110, 60, 30, 10]

    result = evaluator.evaluate(
        strategy_id="s2",
        trade_pnls=trades,
        equity_curve=equity,
        window=5,
    )

    assert result.health_score < 0.5
    assert "DRAWDOWN_RISK" in result.flags


def test_insufficient_trades_flagged():
    evaluator = StrategyHealthEvaluator(min_trades=20)
    trades = [5, -3, 4]
    equity = [100, 105, 102]

    result = evaluator.evaluate(
        strategy_id="s3",
        trade_pnls=trades,
        equity_curve=equity,
        window=10,
    )

    assert "INSUFFICIENT_TRADES" in result.flags
