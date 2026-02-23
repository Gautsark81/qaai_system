from datetime import datetime

from core.v2.paper_trading.contracts import PaperFill
from core.v2.paper_trading.pnl.ledger import PnLLedger
from core.v2.paper_trading.pnl.attribution import PnLAttribution


def test_pnl_ledger_records_buy_and_sell():
    ledger = PnLLedger()

    buy = PaperFill(
        fill_id="f1",
        order_id="o1",
        symbol="AAPL",
        side="BUY",
        quantity=10,
        price=100.0,
        filled_at=datetime.utcnow(),
    )

    sell = PaperFill(
        fill_id="f2",
        order_id="o2",
        symbol="AAPL",
        side="SELL",
        quantity=5,
        price=110.0,
        filled_at=datetime.utcnow(),
    )

    ledger.record(fill=buy, strategy_id="s1")
    ledger.record(fill=sell, strategy_id="s1")

    entries = ledger.entries()
    assert len(entries) == 2
    assert entries[0].delta == -1000.0
    assert entries[1].delta == 550.0


def test_pnl_attribution():
    ledger = PnLLedger()
    attr = PnLAttribution()

    ledger.record(
        fill=PaperFill(
            fill_id="f1",
            order_id="o1",
            symbol="AAPL",
            side="BUY",
            quantity=1,
            price=100.0,
            filled_at=datetime.utcnow(),
        ),
        strategy_id="s1",
    )

    ledger.record(
        fill=PaperFill(
            fill_id="f2",
            order_id="o2",
            symbol="MSFT",
            side="SELL",
            quantity=2,
            price=50.0,
            filled_at=datetime.utcnow(),
        ),
        strategy_id="s2",
    )

    entries = ledger.entries()

    by_strategy = attr.by_strategy(entries)
    by_symbol = attr.by_symbol(entries)

    assert by_strategy["s1"] == -100.0
    assert by_strategy["s2"] == 100.0
    assert by_symbol["AAPL"] == -100.0
    assert by_symbol["MSFT"] == 100.0
