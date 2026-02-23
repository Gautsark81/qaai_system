# tests/strategy_tournament/test_gates.py

from modules.strategy_tournament.gates import HardGateEvaluator
from modules.strategy_tournament.metrics import SymbolMetrics
from modules.strategy_tournament.aggregations import StrategyMetrics


def test_hard_gate_pass():
    strategy_metrics = StrategyMetrics(
        strategy_id="s1",
        symbols_traded=2,
        total_trades=50,
        total_wins=30,
        total_losses=20,
        overall_win_rate=0.6,
        total_pnl=500,
        max_drawdown=4,
    )

    symbol_metrics = [
        SymbolMetrics("A", 25, 15, 10, 0.6, 300, 3),
        SymbolMetrics("B", 25, 15, 10, 0.6, 200, 4),
    ]

    gate = HardGateEvaluator(
        min_trades=30,
        min_ssr=0.8,
        max_drawdown=5,
    )

    decision = gate.evaluate(strategy_metrics, symbol_metrics)
    assert decision.is_pass is True
    assert decision.failed_reasons == []


def test_hard_gate_fail_multiple_reasons():
    strategy_metrics = StrategyMetrics(
        strategy_id="s2",
        symbols_traded=1,
        total_trades=10,
        total_wins=4,
        total_losses=6,
        overall_win_rate=0.4,
        total_pnl=-50,
        max_drawdown=12,
    )

    symbol_metrics = [
        SymbolMetrics("A", 10, 4, 6, 0.4, -50, 12),
    ]

    gate = HardGateEvaluator(
        min_trades=30,
        min_ssr=0.8,
        max_drawdown=5,
    )

    decision = gate.evaluate(strategy_metrics, symbol_metrics)

    assert decision.is_pass is False
    assert "total_trades<30" in decision.failed_reasons
    assert "SSR<0.8" in decision.failed_reasons
    assert "max_drawdown>5" in decision.failed_reasons
