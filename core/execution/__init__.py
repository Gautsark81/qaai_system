"""
Execution public API.

Only stable, externally-consumable execution primitives
are exposed here. Internal helpers must NOT leak.
"""
from .engine import ExecutionEngine
from .idempotency_ledger.ledger import ExecutionIdempotencyLedger

# ---- Core execution engine ----
from core.execution.engine import ExecutionEngine

# ---- Idempotency ----
from core.execution.idempotency_ledger.ledger import ExecutionIdempotencyLedger

# ---- Execution intent contract ----
from core.execution.execution_intent import ExecutionIntent

__all__ = [
    "ExecutionEngine",
    "ExecutionIdempotencyLedger",
    "ExecutionIntent",
]
