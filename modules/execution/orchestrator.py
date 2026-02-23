# modules/execution/orchestrator.py

"""
Phase 9 Production Execution Orchestrator.

STRICT GUARANTEES:
- Idempotent order submission
- Deterministic execution
- No side effects before broker validation
- Performance instrumentation is observational ONLY
"""

from modules.performance.timers import timed
from modules.performance.registry import PerformanceRegistry


_perf_registry = PerformanceRegistry()


class ExecutionOrchestrator:
    """
    Phase 9 execution engine.

    This class is intentionally minimal.
    Strategy logic, risk logic, and capital logic
    MUST NOT appear here.
    """

    def __init__(self, broker, state_store, config):
        self.broker = broker
        self.state_store = state_store
        self.config = config

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def start(self):
        """
        Entry point after full bootstrap validation.

        Phase 9 does NOT define event loops.
        """
        print("[EXECUTION STARTED]")

    def submit_order(self, order_id: str, order_payload: dict):
        """
        Submit an order in an idempotent, observable manner.
        """
        # ---- Idempotency gate
        if self.state_store.is_order_open(order_id):
            return

        # ---- Broker submission (observed, not modified)
        with timed() as elapsed:
            self.broker.submit(order_payload)

        _perf_registry.record("execution_submit", elapsed())

        # ---- Persist only AFTER successful submission
        self.state_store.persist_open_order(order_id)
