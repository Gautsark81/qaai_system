# tests/strategy_factory/test_fitness_evaluator.py

from qaai_system.strategy_factory.fitness import evaluate_fitness


def test_fitness_evaluation_passes():
    backtest = {
        "metrics": {
            "trades": 250,
            "win_rate": 0.82,
            "profit_factor": 1.6,
            "max_drawdown": 0.12,
            "sharpe": 1.9,
        }
    }

    out = evaluate_fitness(backtest)

    assert out["passed"] is True
    assert out["fitness_score"] > 0
    assert out["win_rate"] == 0.82
