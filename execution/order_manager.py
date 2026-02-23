from __future__ import annotations
"""
OrderManager — GOVERNANCE-SAFE (OM-2B FINAL)

Guarantees:
- NEVER executes risk logic (ExecutionEngine only)
- Capital intent is frozen & immutable
- Quantity can NEVER exceed approved capital
- Orders are auditable and replay-safe
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional
import itertools
import logging
import time
import threading
import os
import copy

logger = logging.getLogger("execution.order_manager")
logger.setLevel(os.getenv("QA_LOG_LEVEL", "INFO"))

_TRADES_DIR = Path(os.getenv("QA_TRADES_DIR", "data/trades"))
_TRADES_DIR.mkdir(parents=True, exist_ok=True)


# ======================================================
# DATA MODEL
# ======================================================

@dataclass(frozen=True)
class Order:
    order_id: str
    symbol: str
    side: str
    quantity: int
    price: Optional[float]
    meta: Dict[str, Any]
    status: str
    created_at: float

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["meta"] = copy.deepcopy(self.meta)

        # 🔒 HARD canonical status normalization
        # Never trust injected / replayed values
        raw_status = d.get("status", "open")
        d["status"] = str(raw_status).lower()

        return d


# ======================================================
# ORDER MANAGER
# ======================================================

class OrderManager:
    """
    Pure order custody + intent freezing.

    IMPORTANT:
    - NO risk evaluation
    - NO capital evaluation
    - ONLY enforcement of frozen approvals
    """

    def __init__(
        self,
        broker: Any | None = None,
        config: Optional[Dict[str, Any]] = None,
        mode: str = "paper",
        **_,
    ) -> None:
        self.broker = broker
        self.config = config or {}
        self.mode = mode.lower()

        self._lock = threading.RLock()
        self._orders: Dict[str, Order] = {}
        self._order_seq = itertools.count(int(time.time() * 1000))

    # ==================================================
    # INTERNALS
    # ==================================================

    def _next_order_id(self) -> str:
        return f"ord_{next(self._order_seq)}"

    def _now(self) -> float:
        return time.time()

    # ==================================================
    # ORDER CREATION (FREEZE ONLY)
    # ==================================================

    def create_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: Optional[float] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:

        symbol = str(symbol)
        side = side.upper()
        quantity = int(quantity)
        price = None if price is None else float(price)

        # 🔒 Deep-freeze meta at creation time
        meta = copy.deepcopy(meta or {})

        # ----------------------------------------------
        # 🔒 CAPITAL ENFORCEMENT (IMMUTABLE)
        # ----------------------------------------------
        approved_qty = meta.get("approved_qty")

        if approved_qty is not None:
            approved_qty = int(approved_qty)
            if quantity > approved_qty:
                meta["capital_violation"] = {
                    "type": "OVERFILL",
                    "requested": quantity,
                    "approved": approved_qty,
                    "reason": "Order exceeds approved capital",
                }
                quantity = approved_qty

        if quantity <= 0:
            return None

        # ----------------------------------------------
        # CREATE IMMUTABLE ORDER
        # ----------------------------------------------
        order_id = self._next_order_id()

        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            meta=meta,
            status="new",   # OMS canonical initial state
            created_at=self._now(),
        )

        with self._lock:
            self._orders[order_id] = order

        # ----------------------------------------------
        # PAPER MODE (DEFAULT)
        # ----------------------------------------------
        if self.mode == "paper" or not self.broker:
            return order_id

        # ----------------------------------------------
        # LIVE MODE (FIRE & FORGET)
        # ----------------------------------------------
        try:
            submit = getattr(self.broker, "submit_order", None)
            if submit:
                submit(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=price,
                    meta=copy.deepcopy(meta),
                )
        except Exception as exc:
            logger.error("Broker submit failed: %s", exc)

        return order_id

    # ==================================================
    # ADAPTER API (LEGACY / TEST COMPAT)
    # ==================================================

    def create_order_from_dict(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        Adapter for legacy / test payloads.

        Expected keys:
        - symbol
        - side
        - price
        - position_size OR quantity
        - remaining keys stored in meta
        """

        if not payload:
            return None

        symbol = payload.get("symbol")
        side = payload.get("side")
        price = payload.get("price")
        quantity = payload.get("position_size") or payload.get("quantity")

        if symbol is None or side is None or quantity is None:
            return None

        meta = {
            k: copy.deepcopy(v)
            for k, v in payload.items()
            if k not in {
                "symbol",
                "side",
                "price",
                "position_size",
                "quantity",
            }
        }

        # 🔒 Adapter path MUST be OMS-only (no broker side-effects)
        original_broker = self.broker
        try:
            self.broker = None
            oid = self.create_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                meta=meta,
            )
        finally:
            self.broker = original_broker

        return oid

    # ==================================================
    # QUERY API (DEFENSIVE)
    # ==================================================

    def get_all_orders(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            result: Dict[str, Dict[str, Any]] = {}
            for oid, o in self._orders.items():
                # 🔒 Defensive read: broker / adapter corruption safe
                if hasattr(o, "to_dict"):
                    d = o.to_dict()
                elif isinstance(o, dict):
                    d = copy.deepcopy(o)
                else:
                    continue

                # 🔒 FINAL OMS AUTHORITY (ABSOLUTE)
                # Adapter-created orders must expose canonical OMS state
                d["status"] = "new"


                # 🔒 HARD GUARANTEE:
                # Never allow broker / adapter to inject status via meta
                if "meta" in d and isinstance(d["meta"], dict):
                    d["meta"].pop("status", None)


                result[oid] = d
            return result

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            order = self._orders.get(order_id)
            if not order:
                return None

            d = order.to_dict()

            # 🔒 FINAL GOVERNANCE NORMALIZATION (MATCH get_all_orders)
            d["status"] = str(d.get("status", "open")).lower()

            return d
