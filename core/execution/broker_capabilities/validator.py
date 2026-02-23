# core/execution/broker_capabilities/validator.py

from typing import Iterable
from core.execution.broker_capabilities.contracts import BrokerCapabilities


class UnsupportedBrokerOperation(Exception):
    pass


class BrokerCapabilityValidator:
    """
    Deterministic validator.

    No execution.
    No IO.
    Pure rejection logic.
    """

    @staticmethod
    def validate_required_operations(
        *,
        broker: BrokerCapabilities,
        required_operations: Iterable[str],
    ) -> None:
        supported = broker.supported_operations()

        for op in required_operations:
            if op not in supported:
                raise UnsupportedBrokerOperation(
                    f"Broker '{broker.broker_name}' does not support '{op}'"
                )
