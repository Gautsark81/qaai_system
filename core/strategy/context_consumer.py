# core/strategy/context_consumer.py

from typing import Optional, Iterable, Dict, Any
from copy import deepcopy
from functools import wraps
from types import MappingProxyType


class ReadOnlyDict(dict):
    """
    Immutable, deepcopy-safe dictionary.
    Execution-safe metadata container.
    """

    def __readonly__(self, *args, **kwargs):
        raise TypeError("Context metadata is read-only")

    __setitem__ = __readonly__
    __delitem__ = __readonly__
    clear = __readonly__
    pop = __readonly__
    popitem = __readonly__
    setdefault = __readonly__
    update = __readonly__

    def __deepcopy__(self, memo):
        return self


# Context keys NEVER allowed in execution metadata
_EXECUTION_EXCLUDED_CONTEXT_KEYS = {
    "risk_signals",
    "risk_explanation",
    "capital_view",
    "risk_view",
    "governance_notes",
}


class ContextAwareStrategy:
    """
    Passive context consumer mixin.

    RULES (LOCKED):
    - Strategies may READ full context
    - Orders are NOT modified unless explicitly allowed
    - Advisory intelligence NEVER alters execution output
    """

    __slots__ = ("_context_provider",)

    # 🔒 Explicit opt-in switch
    ATTACH_CONTEXT_TO_ORDERS = False

    def __init__(self, context_provider=None, *args, **kwargs):
        self._context_provider = context_provider
        super().__init__(*args, **kwargs)

    # ─────────────────────────────────────────────
    # Context access (READ-ONLY)
    # ─────────────────────────────────────────────

    def context_snapshot(self, symbol: str) -> Optional[dict]:
        if self._context_provider is None:
            return None
        return self._context_provider.get(symbol)

    # ─────────────────────────────────────────────
    # Execution-safe projection
    # ─────────────────────────────────────────────

    def _execution_context(self, symbol: str) -> Optional[MappingProxyType]:
        snap = self.context_snapshot(symbol)
        if snap is None:
            return None

        filtered = {
            k: v for k, v in snap.items()
            if k not in _EXECUTION_EXCLUDED_CONTEXT_KEYS
        }

        return MappingProxyType(filtered)

    # ─────────────────────────────────────────────
    # Optional annotation
    # ─────────────────────────────────────────────

    def _annotate_orders_with_context(
        self,
        orders: Iterable[Dict[str, Any]],
    ) -> Iterable[Dict[str, Any]]:

        # 🚨 DEFAULT: do nothing
        if not self.ATTACH_CONTEXT_TO_ORDERS:
            return orders

        annotated = []

        for order in orders:
            order_copy = deepcopy(order)

            symbol = order_copy.get("symbol")
            exec_ctx = self._execution_context(symbol)

            if exec_ctx is not None:
                order_copy["context"] = ReadOnlyDict(exec_ctx)

            annotated.append(order_copy)

        return annotated

    # ─────────────────────────────────────────────
    # Safe auto-wrapping
    # ─────────────────────────────────────────────

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if "generate_orders" not in cls.__dict__:
            return

        original_generate = cls.__dict__["generate_orders"]

        @wraps(original_generate)
        def wrapped_generate(self, *args, **kwargs):
            orders = original_generate(self, *args, **kwargs)
            return self._annotate_orders_with_context(orders)

        cls.generate_orders = wrapped_generate
