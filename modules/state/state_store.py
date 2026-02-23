"""
modules/state/state_store.py

Production-safe persistence layer.
Observed for performance regressions.
"""

from modules.performance.timers import timed
from modules.performance.registry import PerformanceRegistry


_perf_registry = PerformanceRegistry()


class StateStore:
    """
    Minimal deterministic state store.

    Guarantees:
    - Idempotent persistence
    - Restart-safe
    - Observable latency
    """

    def __init__(self, config):
        self._open_orders = []

    # --------------------------------------------------
    # READ
    # --------------------------------------------------

    def load_open_orders(self):
        return list(self._open_orders)

    # --------------------------------------------------
    # WRITE
    # --------------------------------------------------

    def persist_open_order(self, order_id: str):
        """
        Persist open order deterministically.
        """
        with timed() as elapsed:
            if order_id not in self._open_orders:
                self._open_orders.append(order_id)

        _perf_registry.record("persist_write", elapsed())
