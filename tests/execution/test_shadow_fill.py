from datetime import datetime

from qaai_system.execution.shadow_fill import ShadowFillEngine
from data.execution.intent import ExecutionIntent


class FixedPriceSource:
    """
    Deterministic price source for testing.
    """

    def __init__(self, price: float):
        self._price = price

    def price_at(self, symbol: str, ts: datetime) -> float:
        return self._price


def _intent(side="BUY"):
    return ExecutionIntent(
        strategy_id="strat1",
        symbol="NIFTY",
        side=side,
        quantity=10,
        order_type="MARKET",
        price=None,
        signal_time=datetime(2025, 1, 1, 9, 15),
        feature_manifest_id="fm1",
        model_id="m1",
    )


def test_shadow_fill_buy_no_slippage():
    engine = ShadowFillEngine(
        price_source=FixedPriceSource(100.0),
        slippage_bps=0.0,
    )

    fill = engine.fill(_intent("BUY"))

    assert fill.fill_price == 100.0
    assert fill.quantity == 10
    assert fill.side == "BUY"


def test_shadow_fill_buy_with_slippage():
    engine = ShadowFillEngine(
        price_source=FixedPriceSource(100.0),
        slippage_bps=10.0,  # 10 bps = 0.10%
    )

    fill = engine.fill(_intent("BUY"))

    assert fill.fill_price == 100.1


def test_shadow_fill_sell_with_slippage():
    engine = ShadowFillEngine(
        price_source=FixedPriceSource(100.0),
        slippage_bps=10.0,
    )

    fill = engine.fill(_intent("SELL"))

    assert fill.fill_price == 99.9


def test_shadow_fill_is_deterministic():
    engine = ShadowFillEngine(
        price_source=FixedPriceSource(100.0),
        slippage_bps=5.0,
    )

    intent = _intent("BUY")

    f1 = engine.fill(intent)
    f2 = engine.fill(intent)

    assert f1 == f2
