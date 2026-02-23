from datetime import datetime
from domain.broker.broker_trade_snapshot import BrokerTradeSnapshot


def test_broker_trade_snapshot_fields():
    snap = BrokerTradeSnapshot(
        order_id="OID1",
        symbol="NIFTY",
        side="BUY",
        executed_qty=1,
        executed_price=20000,
        executed_value=20000,
        executed_at=datetime.utcnow(),
    )
    assert snap.executed_value == 20000
