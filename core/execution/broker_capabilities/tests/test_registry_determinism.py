from core.execution.broker_capabilities.contracts import BrokerCapabilities
from core.execution.broker_capabilities.registry import BrokerCapabilityRegistry


def test_registry_snapshot_is_deterministic():
    reg = BrokerCapabilityRegistry()

    reg.register(
        BrokerCapabilities(
            broker_name="B",
            version="1",
            supports_market_orders=True,
            supports_limit_orders=True,
            supports_intraday=True,
            supports_bracket_orders=False,
            supports_partial_fills=False,
            supports_live_position_query=True,
            supports_cancel_replace=False,
            supports_replay=True,
        )
    )

    reg.register(
        BrokerCapabilities(
            broker_name="A",
            version="1",
            supports_market_orders=True,
            supports_limit_orders=True,
            supports_intraday=True,
            supports_bracket_orders=True,
            supports_partial_fills=True,
            supports_live_position_query=True,
            supports_cancel_replace=True,
            supports_replay=True,
        )
    )

    snapshot_keys = list(reg.snapshot().keys())
    assert snapshot_keys == ["A", "B"]
