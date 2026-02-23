import pytest
from qaai_system.paper_trading.broker import PaperBroker


def test_bracket_stop_loss_triggers():
    br = PaperBroker(
        starting_cash=10_000.0,
        slippage_bps=0,
        spread_bps=0,
        max_drawdown_pct=1.0,
        max_positions=10,
        max_exposure_pct=1.0,
    )
    # open long 100 @ 100, SL=95
    br.open_long(
        "SYM", mid_price=100.0, qty=100, mid_prices_view={"SYM": 100.0}, stop_loss=95.0
    )
    # price drops to 94 -> SL triggers on update
    br.update_prices({"SYM": 94.0})
    assert "SYM" not in br.positions
    assert br.realized_pnl == pytest.approx((94.0 - 100.0) * 100, rel=1e-9)


def test_bracket_take_profit_triggers():
    br = PaperBroker(
        starting_cash=10_000.0,
        slippage_bps=0,
        spread_bps=0,
        max_drawdown_pct=1.0,
        max_positions=10,
        max_exposure_pct=1.0,
    )
    br.open_long(
        "ABC",
        mid_price=100.0,
        qty=50,
        mid_prices_view={"ABC": 100.0},
        take_profit=105.0,
    )
    br.update_prices({"ABC": 106.0})
    assert "ABC" not in br.positions
    assert br.realized_pnl == pytest.approx((106.0 - 100.0) * 50, rel=1e-9)


def test_trailing_stop_triggers_from_peak():
    br = PaperBroker(
        starting_cash=10_000.0,
        slippage_bps=0,
        spread_bps=0,
        max_drawdown_pct=1.0,
        max_positions=10,
        max_exposure_pct=1.0,
    )
    br.open_long(
        "TS", mid_price=100.0, qty=10, mid_prices_view={"TS": 100.0}, trailing_pct=0.05
    )  # 5%
    # run up to 120 → trailing stop becomes 120 * 0.95 = 114
    br.update_prices({"TS": 120.0})
    # drop to 113 -> below trailing stop -> exit
    br.update_prices({"TS": 113.0})
    assert "TS" not in br.positions
    assert br.realized_pnl == pytest.approx((113.0 - 100.0) * 10, rel=1e-9)


def test_max_positions_enforced():
    br = PaperBroker(
        starting_cash=10_000.0,
        slippage_bps=0,
        spread_bps=0,
        max_drawdown_pct=1.0,
        max_positions=1,
        max_exposure_pct=1.0,
    )
    br.open_long("ONE", mid_price=100.0, qty=10, mid_prices_view={"ONE": 100.0})
    with pytest.raises(ValueError):
        br.open_long(
            "TWO", mid_price=50.0, qty=10, mid_prices_view={"ONE": 100.0, "TWO": 50.0}
        )


def test_drawdown_halts_trading():
    # 1% drawdown cap to make it easy to trigger
    br = PaperBroker(
        starting_cash=10_000.0,
        slippage_bps=0,
        spread_bps=0,
        max_drawdown_pct=0.01,
        max_positions=10,
        max_exposure_pct=1.0,
    )
    # buy 50 @ 100 -> equity 10k
    br.open_long("DROP", mid_price=100.0, qty=50, mid_prices_view={"DROP": 100.0})
    # price falls to 90 -> equity ~ 9,500 => 5% drawdown -> halt
    br.update_prices({"DROP": 90.0})
    assert br.trading_halted is True
    # attempt a new trade -> rejected
    with pytest.raises(ValueError):
        br.open_long(
            "NEW", mid_price=10.0, qty=10, mid_prices_view={"DROP": 90.0, "NEW": 10.0}
        )


def test_exposure_cap_blocks_oversized_trade():
    # exposure cap 30%
    br = PaperBroker(
        starting_cash=10_000.0,
        slippage_bps=0,
        spread_bps=0,
        max_drawdown_pct=1.0,
        max_positions=10,
        max_exposure_pct=0.30,
    )
    # Try to open 40 @ 100 -> notional 4,000 => 40% of equity -> reject
    with pytest.raises(ValueError):
        br.open_long("BIG", mid_price=100.0, qty=40, mid_prices_view={"BIG": 100.0})
    # 20 @ 100 -> 2,000 => 20% of equity -> allowed
    br.open_long("OK", mid_price=100.0, qty=20, mid_prices_view={"OK": 100.0})
    assert br.positions["OK"].qty == 20
