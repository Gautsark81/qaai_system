from datetime import datetime, timedelta

from qaai_system.execution.shadow_pnl import ShadowPnLEngine
from qaai_system.execution.shadow_fill import ShadowFill


class FixedExitPriceSource:
    """
    Deterministic exit price for testing.
    """

    def __init__(self, price: float):
        self._price = price

    def exit_price_at(self, symbol: str, entry_ts: datetime) -> float:
        return self._price


def _fill(side="BUY"):
    return ShadowFill(
        intent_id="i1",
        symbol="NIFTY",
        side=side,
        quantity=10,
        fill_price=100.0,
        slippage_bps=0.0,
        fill_ts=datetime(2025, 1, 1, 9, 15),
    )


def test_shadow_pnl_buy_profit():
    engine = ShadowPnLEngine(
        exit_price_source=FixedExitPriceSource(105.0),
        fee_bps=0.0,
    )

    pnl = engine.compute(
        _fill("BUY"),
        exit_ts=datetime(2025, 1, 1, 9, 20),
    )

    assert pnl.gross_pnl == 50.0
    assert pnl.net_pnl == 50.0


def test_shadow_pnl_sell_profit():
    engine = ShadowPnLEngine(
        exit_price_source=FixedExitPriceSource(95.0),
        fee_bps=0.0,
    )

    pnl = engine.compute(
        _fill("SELL"),
        exit_ts=datetime(2025, 1, 1, 9, 20),
    )

    assert pnl.gross_pnl == 50.0


def test_shadow_pnl_with_fees():
    engine = ShadowPnLEngine(
        exit_price_source=FixedExitPriceSource(105.0),
        fee_bps=10.0,  # 10 bps
    )

    pnl = engine.compute(
        _fill("BUY"),
        exit_ts=datetime(2025, 1, 1, 9, 20),
    )

    # Notional = 100 * 10 = 1000
    # Fees = 0.10% = 1.0
    assert pnl.fees == 1.0
    assert pnl.net_pnl == 49.0


def test_shadow_pnl_holding_period():
    engine = ShadowPnLEngine(
        exit_price_source=FixedExitPriceSource(100.0),
    )

    start = datetime(2025, 1, 1, 9, 15)
    end = start + timedelta(minutes=7)

    pnl = engine.compute(
        _fill("BUY"),
        exit_ts=end,
    )

    assert pnl.holding_period_sec == 420
