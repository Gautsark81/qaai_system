# clients/async_order_manager.py
"""
AsyncOrderManager: async wrapper around the synchronous OrderManager.
Provides coroutine-based place_order/get_order_status/cancel_order that do not block
the asyncio event loop. Uses loop.run_in_executor under the hood.
"""

from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class AsyncOrderManager:
    def __init__(self, order_manager, executor: Optional[ThreadPoolExecutor] = None):
        """
        order_manager: an instance of synchronous OrderManager
        executor: optional ThreadPoolExecutor for running blocking calls
        """
        self._om = order_manager
        self._executor = executor or ThreadPoolExecutor(max_workers=4)

    async def place_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: Optional[float] = None,
        order_type: str = "LIMIT",
        idempotency_key: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: self._om.place_order(symbol, side, qty, price=price, order_type=order_type, idempotency_key=idempotency_key, **kwargs),
        )

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, lambda: self._om.cancel_order(order_id))

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, lambda: self._om.get_order_status(order_id))

    # synchronous accessors (pass-through) for convenience
    def sync(self):
        """Expose the underlying synchronous manager if needed."""
        return self._om
