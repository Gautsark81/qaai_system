import pytest

from core.execution.broker_capabilities.contracts import BrokerCapabilities
from core.execution.broker_capabilities.validator import (
    BrokerCapabilityValidator,
    UnsupportedBrokerOperation,
)


def test_validator_blocks_missing_capability():
    caps = BrokerCapabilities(
        broker_name="TEST",
        version="1",
        supports_market_orders=False,
        supports_limit_orders=True,
        supports_intraday=True,
        supports_bracket_orders=False,
        supports_partial_fills=False,
        supports_live_position_query=True,
        supports_cancel_replace=False,
        supports_replay=True,
    )

    with pytest.raises(UnsupportedBrokerOperation):
        BrokerCapabilityValidator.validate_required_operations(
            broker=caps,
            required_operations=["MARKET_ORDER"],
        )
