from datetime import datetime
from domain.broker.broker_position_snapshot import BrokerPositionSnapshot


def test_broker_position_snapshot_fields():
    snap = BrokerPositionSnapshot(
        symbol="NIFTY",
        quantity=2,
        average_price=19500,
        market_value=39000,
        as_of=datetime.utcnow(),
    )
    assert snap.quantity == 2
