from core.shadow.execution.shadow_execution_engine import ShadowExecutionEngine
from core.shadow.execution.shadow_order import ShadowOrder, ShadowOrderSide


def test_shadow_buy_sell_roundtrip():
    engine = ShadowExecutionEngine()

    engine.process_order(
        ShadowOrder("s1", "RELIANCE", ShadowOrderSide.BUY, 10, 100.0)
    )
    engine.process_order(
        ShadowOrder("s1", "RELIANCE", ShadowOrderSide.SELL, 10, 110.0)
    )

    pos = engine.positions["RELIANCE"]
    assert pos.quantity == 0
    assert pos.avg_price == 0.0


def test_shadow_mark_to_market():
    engine = ShadowExecutionEngine()

    engine.process_order(
        ShadowOrder("s1", "INFY", ShadowOrderSide.BUY, 5, 1000.0)
    )

    engine.mark_to_market({"INFY": 1050.0})

    assert engine.pnl.unrealized == 250.0
