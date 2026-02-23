# tests/test_paper_broker_brackets_and_trailing.py
import pytest
from qaai_system.paper_trading.broker import PaperBroker


def test_bracket_tp_cancels_sl():
    br = PaperBroker(
        starting_cash=10_000.0,
        slippage_bps=0,
        spread_bps=0,
        max_drawdown_pct=1.0,
        max_positions=10,
        max_exposure_pct=1.0,
    )
    # buy 10 @100, SL=95, TP=105
    br.bracket_buy(
        "A",
        mid_price=100.0,
        qty=10,
        mid_prices_view={"A": 100.0},
        stop_loss=95.0,
        take_profit=105.0,
    )
    # price moves to 106 -> TP should trigger and position removed, bracket gone
    br.update_prices({"A": 106.0})
    assert "A" not in br.positions
    assert "A" not in br.brackets


def test_bracket_sl_triggers_and_tp_canceled():
    br = PaperBroker(
        starting_cash=10_000.0,
        slippage_bps=0,
        spread_bps=0,
        max_drawdown_pct=1.0,
        max_positions=10,
        max_exposure_pct=1.0,
    )
    br.bracket_buy(
        "B",
        mid_price=100.0,
        qty=5,
        mid_prices_view={"B": 100.0},
        stop_loss=90.0,
        take_profit=110.0,
    )
    # drop to 89 -> SL triggers
    br.update_prices({"B": 89.0})
    assert "B" not in br.positions
    assert "B" not in br.brackets
    # realized pnl should be (89 - 100) * 5
    assert br.realized_pnl == pytest.approx((89.0 - 100.0) * 5, rel=1e-9)


def test_trailing_stop_ratchets_and_triggers():
    br = PaperBroker(
        starting_cash=10_000.0,
        slippage_bps=0,
        spread_bps=0,
        max_drawdown_pct=1.0,
        max_positions=10,
        max_exposure_pct=1.0,
    )
    br.bracket_buy(
        "T",
        mid_price=100.0,
        qty=10,
        mid_prices_view={"T": 100.0},
        stop_loss=None,
        take_profit=None,
        trailing_pct=0.05,
    )
    # price rises to 120: highest_seen=120; trailing stop = 120*(1-0.05)=114
    br.update_prices({"T": 120.0})
    # price drops to 113 -> should trigger trailing stop exit
    br.update_prices({"T": 113.0})
    assert "T" not in br.positions
    assert "T" not in br.brackets
    # realized pnl should equal (113 - 100) * 10
    assert br.realized_pnl == pytest.approx((113.0 - 100.0) * 10, rel=1e-9)
