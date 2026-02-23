"""
Strategy lifecycle package.

- Phase-9 lifecycle (offline autonomy)
- Legacy lifecycle re-exported for compatibility
"""

# ---- Legacy lifecycle (explicit, non-conflicting) ----
from core.strategy_factory.legacy_lifecycle import promote

# ---- Phase-9 lifecycle ----
from .state_machine import LifecycleState
from .events import LifecycleEvent
from .lifecycle_engine import LifecycleEngine
from .phase_constraints import assert_execution_allowed
from .evidence_emitter import emit_lifecycle_transition_evidence


__all__ = [
    "promote",
    "LifecycleState",
    "LifecycleEvent",
    "LifecycleEngine",
    "assert_execution_allowed",
    "emit_lifecycle_transition_evidence",
]