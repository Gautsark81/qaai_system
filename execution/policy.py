# File: qaai_system/execution/policy.py
from __future__ import annotations
from typing import Dict, Any, List


class DefaultRoutingPolicy:
    """
    Default routing policy: converts a high-level order plan into one or more
    executable child orders.

    Responsibilities:
      - Normalize qty/quantity keys
      - Enforce sensible defaults (order_type, TIF)
      - Support slicing into multiple chunks (VWAP-style splitting)
      - Allow extension for advanced strategies (iceberg, bracket, etc.)
    """

    def build_order_requests(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Given a plan dict (symbol, side, qty/quantity, price, etc.),
        return a list of child order dicts ready to submit.

        Example input:
            {"symbol": "AAPL", "side": "buy", "qty": 100, "price": 150.0, "slices": 4}

        Example output:
            [
              {"symbol": "AAPL", "side": "buy", "quantity": 25, "order_type": "MKT", "limit_price": None, "tif": "DAY"},
              {"symbol": "AAPL", "side": "buy", "quantity": 25, "order_type": "MKT", "limit_price": None, "tif": "DAY"},
              ...
            ]
        """
        symbol = plan.get("symbol")
        side = plan.get("side")
        qty = plan.get("quantity") or plan.get("qty") or 0
        price = plan.get("price")

        try:
            qty = int(qty)
        except Exception:
            qty = 0

        if qty <= 0:
            return []

        # Build base child order
        order_template: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "quantity": qty,
            "order_type": plan.get("order_type", "MKT"),
            "limit_price": plan.get(
                "limit_price", price if plan.get("order_type") == "LMT" else None
            ),
            "tif": plan.get("tif", "DAY"),
        }

        # If no slicing requested
        slices = int(plan.get("slices", 1) or 1)
        if slices <= 1:
            return [order_template]

        # Split qty evenly across slices, distribute remainder
        base_qty = qty // slices
        remainder = qty % slices
        child_orders: List[Dict[str, Any]] = []

        for i in range(slices):
            q = base_qty + (1 if i < remainder else 0)
            if q <= 0:
                continue
            child = dict(order_template)
            child["quantity"] = q
            child_orders.append(child)

        return child_orders


class VWAPRoutingPolicy(DefaultRoutingPolicy):
    """
    Example VWAP policy: splits order into time-based slices.
    (Stub implementation — extend in Phase 1+ with actual volume curves.)
    """

    def build_order_requests(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        slices = int(plan.get("slices", 4) or 4)
        return super().build_order_requests({**plan, "slices": slices})


class IcebergRoutingPolicy(DefaultRoutingPolicy):
    """
    Example Iceberg policy: only expose a small chunk at a time.
    (Stub — actual iceberg handling would re-queue remainder after fills.)
    """

    def build_order_requests(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        display_qty = int(plan.get("display_qty") or 0)
        qty = int(plan.get("quantity") or plan.get("qty") or 0)

        if display_qty > 0 and qty > display_qty:
            chunks: List[Dict[str, Any]] = []
            remaining = qty
            while remaining > 0:
                expose = min(display_qty, remaining)
                chunk = {
                    "symbol": plan.get("symbol"),
                    "side": plan.get("side"),
                    "quantity": expose,
                    "order_type": plan.get("order_type", "MKT"),
                    "limit_price": plan.get("limit_price", plan.get("price")),
                    "tif": plan.get("tif", "DAY"),
                }
                chunks.append(chunk)
                remaining -= expose
            return chunks

        return super().build_order_requests(plan)
