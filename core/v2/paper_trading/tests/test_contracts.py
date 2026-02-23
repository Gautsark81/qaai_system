from datetime import datetime

from core.v2.paper_trading.contracts import (
    PaperOrder,
    PaperFill,
    PaperTradeCycle,
)


def test_paper_order_is_immutable():
    o = PaperOrder(
        order_id="o1",
        strategy_id="s1",
        symbol="AAPL",
        side="BUY",
        quantity=10,
        created_at=datetime.utcnow(),
    )

    try:
        o.quantity = 20
        mutated = True
    except Exception:
        mutated = False

    assert mutated is False


def test_paper_fill_links_to_order():
    f = PaperFill(
        fill_id="f1",
        order_id="o1",
        symbol="AAPL",
        side="BUY",
        quantity=10,
        price=100.0,
        filled_at=datetime.utcnow(),
    )

    assert f.order_id == "o1"


def test_trade_cycle_structure():
    c = PaperTradeCycle(
        cycle_id="c1",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        orders_created=2,
        fills_created=2,
        pnl_delta=5.0,
    )

    assert c.orders_created == 2
