from __future__ import annotations

import uuid
import inspect
from typing import Any, Dict, Optional


class OrderManager:
    """
    Canonical Order Manager (Phase B1)

    Responsibilities:
    - Order creation & normalization
    - Broker signature adaptation
    - In-memory authoritative registry
    - Deterministic replay compatibility
    - ExecutionEngine-safe semantics
    """

    def __init__(
        self,
        broker: Optional[Any] = None,
        client: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        mode: Optional[str] = None,
    ):
        self.broker = broker or client
        self.config = config or {}

        self.mode = mode or self.config.get("exec_mode", "paper")
        self.approved_for_live = bool(self.config.get("approved_for_live", False))

        # 🔒 HARD SAFETY
        if self.mode == "live" and not self.approved_for_live:
            raise RuntimeError("Live trading not approved")

        # 🔑 Authoritative registry (order_id → order dict)
        self._orders: Dict[str, Dict[str, Any]] = {}

    # ==========================================================
    # PUBLIC API
    # ==========================================================
    def create_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
        }
        if meta:
            payload.update(meta)

        return self._create_order_internal(payload)

    def create_order_from_dict(self, payload: Dict[str, Any]) -> str:
        return self._create_order_internal(dict(payload))

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Return a single order by id (NO COPY).

        Required by:
        - capital freeze tests
        - governance inspection
        - execution validation
        """
        return self._orders.get(order_id)

    def get_all_orders(self) -> Dict[str, Dict[str, Any]]:
        """
        Return authoritative registry.

        IMPORTANT:
        - This is NOT a copy
        - Execution replay relies on identity
        """
        return self._orders

    # ==========================================================
    # INTERNALS
    # ==========================================================
    def _create_order_internal(self, order: Dict[str, Any]) -> str:
        oid = str(uuid.uuid4())

        # ---- normalize quantity ----
        if "qty" in order:
            order.setdefault("quantity", order["qty"])
            order.setdefault("position_size", order["qty"])

        if "quantity" in order:
            order.setdefault("qty", order["quantity"])
            order.setdefault("position_size", order["quantity"])

        # ---- normalize metadata ----
        order.setdefault("filled_qty", 0)
        order.setdefault("status", "NEW")

        # ---- attach identity ----
        order["id"] = oid

        # ---- broker dispatch (side-effect only) ----
        if self.broker is not None:
            self._submit_to_broker(order)

        # 🔑 SINGLE SOURCE OF TRUTH
        self._orders[oid] = order
        return oid

    # ==========================================================
    # BROKER ADAPTER
    # ==========================================================
    def _submit_to_broker(self, order: Dict[str, Any]) -> None:
        submit = getattr(self.broker, "submit_order", None)
        if submit is None:
            return

        sig = inspect.signature(submit)

        try:
            # kwargs broker
            if any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values()):
                submit(**order)
                return

            # dict broker
            if len(sig.parameters) == 1:
                submit(order)
                return

            # positional broker
            submit(
                order.get("symbol"),
                order.get("side"),
                order.get("qty"),
                order.get("price"),
            )
        except Exception:
            # 🔒 OMS must NEVER crash on broker failure
            pass
