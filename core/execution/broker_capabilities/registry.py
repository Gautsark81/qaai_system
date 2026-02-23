# core/execution/broker_capabilities/registry.py

from typing import Dict
from core.execution.broker_capabilities.contracts import BrokerCapabilities


class BrokerCapabilityRegistry:
    """
    Deterministic, in-memory registry.
    """

    def __init__(self) -> None:
        self._registry: Dict[str, BrokerCapabilities] = {}

    def register(self, capabilities: BrokerCapabilities) -> None:
        self._registry[capabilities.broker_name] = capabilities

    def get(self, broker_name: str) -> BrokerCapabilities:
        if broker_name not in self._registry:
            raise KeyError(f"Broker '{broker_name}' is not registered")
        return self._registry[broker_name]

    def snapshot(self) -> Dict[str, BrokerCapabilities]:
        return dict(sorted(self._registry.items()))
