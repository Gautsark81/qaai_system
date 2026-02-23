import pytest

from core.v2.live_bridge.adapters.read_only_broker import (
    ReadOnlyBrokerAdapter,
    ReadOnlyBrokerError,
)


def test_read_only_broker_allows_reads():
    broker = ReadOnlyBrokerAdapter()

    assert broker.get_positions() == []
    assert broker.get_fills() == []
    assert broker.get_pnl() == 0.0


def test_read_only_broker_blocks_trading():
    broker = ReadOnlyBrokerAdapter()

    with pytest.raises(ReadOnlyBrokerError):
        broker.place_order()

    with pytest.raises(ReadOnlyBrokerError):
        broker.modify_order()

    with pytest.raises(ReadOnlyBrokerError):
        broker.cancel_order()
