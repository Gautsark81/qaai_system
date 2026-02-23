# tests/tournament/test_metrics_contract.py

from core.tournament.metrics_builder import build_strategy_metrics


class DummyTrade:
    def __init__(self, pnl: float):
        self.pnl = pnl


def test_metrics_ssr_correct():
    trades = [DummyTrade(10), DummyTrade(-5), DummyTrade(8)]
    equity = [100, 110, 105, 115]

    m = build_strategy_metrics(
        strategy_id="s1",
        trades=trades,
        equity_curve=equity,
        symbol_count=5,
        avg_trade_duration=12.0,
        time_in_market_pct=15.0,
        avg_win=9.0,
        avg_loss=-5.0,
        avg_rr=1.8,
        max_single_loss_pct=2.5,
    )

    assert m.total_trades == 3
    assert m.win_trades == 2
    assert m.loss_trades == 1
    assert abs(m.ssr - (2 / 3)) < 1e-9


def test_zero_trades_safe():
    m = build_strategy_metrics(
        strategy_id="s0",
        trades=[],
        equity_curve=[],
        symbol_count=0,
        avg_trade_duration=0.0,
        time_in_market_pct=0.0,
        avg_win=0.0,
        avg_loss=0.0,
        avg_rr=0.0,
        max_single_loss_pct=0.0,
    )

    assert m.ssr == 0.0
    assert m.total_trades == 0
