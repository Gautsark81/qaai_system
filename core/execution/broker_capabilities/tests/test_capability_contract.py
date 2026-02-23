from core.execution.broker_capabilities.contracts import BrokerCapabilities


def test_supported_operations_mapping():
    caps = BrokerCapabilities(
        broker_name="TEST",
        version="1.0",
        supports_market_orders=True,
        supports_limit_orders=False,
        supports_intraday=True,
        supports_bracket_orders=False,
        supports_partial_fills=False,
        supports_live_position_query=True,
        supports_cancel_replace=False,
        supports_replay=True,
    )

    ops = caps.supported_operations()

    assert "MARKET_ORDER" in ops
    assert "INTRADAY" in ops
    assert "POSITION_QUERY" in ops
    assert "REPLAY" in ops
    assert "LIMIT_ORDER" not in ops
