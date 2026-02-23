# execution/router_core.py

from __future__ import annotations

from typing import Dict, Any


class RouterCore:
    """
    Phase-B Canonical Router Core

    Golden Rules:
    - Routes orders only
    - No risk decisions
    - No audit
    - No execution mode logic
    - No authority outside provider surface
    """

    def __init__(self, provider: Any):
        self.provider = provider

        # ----------------------------------------------------------
        # Normalize provider contract (tests rely on these)
        # ----------------------------------------------------------

        if not hasattr(self.provider, "_positions"):
            self.provider._positions = {}

        if not hasattr(self.provider, "_account_nav"):
            self.provider._account_nav = 0.0

        if not hasattr(self.provider, "orders"):
            self.provider.orders = {}

        if not hasattr(self.provider, "_id_seq"):
            self.provider._id_seq = 0

        if not hasattr(self.provider, "_next_id"):
            self.provider._next_id = self._generate_child_id

    # --------------------------------------------------------------
    # Internal ID management
    # --------------------------------------------------------------

    def _bump_id(self) -> int:
        self.provider._id_seq += 1
        return self.provider._id_seq

    def _generate_child_id(self) -> str:
        return f"child_{self._bump_id()}"

    # --------------------------------------------------------------
    # Order Routing
    # --------------------------------------------------------------

    def submit(self, order: Dict[str, Any]) -> Any:
        """
        Submit order to underlying provider.

        The provider may implement:
            - submit(order)
            - submit_order(order)

        This router does not interpret order semantics.
        """

        if hasattr(self.provider, "submit"):
            return self.provider.submit(order)

        if hasattr(self.provider, "submit_order"):
            return self.provider.submit_order(order)

        raise RuntimeError("Provider has no submit or submit_order method")

    # --------------------------------------------------------------
    # Cancel Routing
    # --------------------------------------------------------------

    def cancel(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel order through provider.

        If provider lacks cancel method,
        perform safe fallback removal from order store.
        """

        if hasattr(self.provider, "cancel"):
            return self.provider.cancel(order_id)

        if hasattr(self.provider, "orders"):
            self.provider.orders.pop(order_id, None)

        return {
            "order_id": order_id,
            "status": "CANCELLED",
        }