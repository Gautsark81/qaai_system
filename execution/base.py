# qaai_system/execution/base.py
"""
Execution provider base contract.

This module defines the minimal, stable interface that ALL execution
providers (paper, live, simulated, dummy) must satisfy.

Design rules:
- Deterministic defaults
- Test-aligned internal state
- No broker-specific logic
- No imports from router/orchestrator/risk
"""

from __future__ import annotations
from typing import Dict, Any, List
import uuid


class ExecutionProvider:
    """
    Base execution provider.

    Tests and higher-level components rely on the following invariants:
    - `_orders` exists and is a dict
    - `_positions` exists and is a dict
    - `_account_nav` exists and is a float
    - `_next_id()` exists and returns `ord_...`
    """

    # -----------------------------
    # Lifecycle
    # -----------------------------
    def __init__(self) -> None:
        # Order state keyed by order_id
        self._orders: Dict[str, Dict[str, Any]] = {}

        # Position state (symbol → qty or provider-defined payload)
        self._positions: Dict[str, Any] = {}

        # Net asset value (used by risk & tests)
        self._account_nav: float = 1_000_000.0

    # -----------------------------
    # ID generation (TEST CRITICAL)
    # -----------------------------
    def _next_id(self) -> str:
        """
        Generate a deterministic-format order ID.

        Tests REQUIRE:
        - prefix: 'ord_'
        - uniqueness per call
        """
        return f"ord_{uuid.uuid4().hex[:8]}"

    # -----------------------------
    # Core order APIs (abstract)
    # -----------------------------
    def submit_order(self, order: Dict[str, Any]) -> Any:
        """
        Submit an order.

        Must return either:
        - order_id: str
        - or dict containing {"order_id": str}
        """
        raise NotImplementedError("submit_order must be implemented by provider")

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a single order.

        Return:
        - True if cancellation succeeded
        - False otherwise
        """
        raise NotImplementedError("cancel_order must be implemented by provider")

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Return current order status.

        Must return a dict containing at least:
        - order_id
        - status (string)
        Optional:
        - symbol
        - filled_qty
        """
        raise NotImplementedError("get_order_status must be implemented by provider")

    # -----------------------------
    # Optional batch / query APIs
    # -----------------------------
    def cancel_all(self) -> List[str]:
        """
        Cancel all open orders.

        Default implementation: no-op.
        """
        return []

    def get_filled_orders(self) -> List[Dict[str, Any]]:
        """
        Return filled child orders.

        Used by orchestrator.poll() to generate PnL feedback.
        Default implementation: none.
        """
        return []

    def fetch_fills_for_order_ids(self, order_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Optional helper for batch fill retrieval.
        """
        return []

    # -----------------------------
    # Reset helper (tests rely on this)
    # -----------------------------
    def reset(self) -> None:
        """
        Reset provider state.

        Tests expect this to:
        - clear orders
        - clear positions
        - restore NAV
        """
        self._orders.clear()
        self._positions.clear()
        self._account_nav = 1_000_000.0
