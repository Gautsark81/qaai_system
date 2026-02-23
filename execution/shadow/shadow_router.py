# execution/shadow/shadow_router.py

from typing import Dict, Any
import uuid
import time


class ShadowRouter:
    """
    Shadow execution router.

    Purpose:
    - Mimic execution semantics
    - NEVER place real orders
    - Deterministic, synchronous, safe

    Used for:
    - Shadow live testing
    - Canary verification
    - End-to-end dry runs
    """

    def submit(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accepts an order dict and returns a filled execution result.
        """

        return {
            "order_id": str(uuid.uuid4()),
            "symbol": order.get("symbol"),
            "qty": order.get("qty"),
            "price": order.get("price"),
            "status": "FILLED",
            "filled_qty": order.get("qty"),
            "filled_price": order.get("price"),
            "timestamp": time.time(),
            "execution_type": "SHADOW",
        }
