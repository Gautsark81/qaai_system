from modules.tournament.promotion_gate import TournamentPromotionGate
from modules.intelligence.metrics import StrategyMetrics


def test_promotion_gate_pass():
    gate = TournamentPromotionGate()

    metrics = StrategyMetrics(
        total_trades=100,
        winning_trades=85,
        losing_trades=15,
        net_pnl=2500,
    )

    req = gate.evaluate(
        strategy_id="strat_1",
        ssr=0.85,
        metrics=metrics,
    )

    assert req is not None
    assert req.stage == "PAPER"


def test_promotion_gate_fail_low_ssr():
    gate = TournamentPromotionGate()

    metrics = StrategyMetrics(
        total_trades=100,
        winning_trades=60,
        losing_trades=40,
        net_pnl=500,
    )

    req = gate.evaluate(
        strategy_id="strat_2",
        ssr=0.6,
        metrics=metrics,
    )

    assert req is None
