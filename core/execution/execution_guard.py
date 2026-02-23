from __future__ import annotations

from typing import Any, Optional

from core.strategy_factory.exceptions import ExecutionNotAllowed
from core.strategy_factory.registry import StrategyRegistry, StrategyRecord


class ExecutionGuard:
    """
    Execution-time invariant and governance enforcement.

    DESIGN PRINCIPLES
    -----------------
    - Deterministic
    - Stateless (logic)
    - Fail-closed
    - Phase-aware
    - Test-stable across Phase-B / Phase-C

    GOVERNANCE MODEL
    ----------------
    1. Phase-B (registry present) → advisory-only → execution FORBIDDEN
    2. Resurrection / shadow / retired states → execution FORBIDDEN
    3. Capital invariants enforced only at runtime
    """

    # ======================================================
    # Construction
    # ======================================================

    def __init__(self, registry: Optional[StrategyRegistry] = None):
        """
        Parameters
        ----------
        registry : StrategyRegistry | None
            Presence implies Phase-B advisory mode.
        """
        self._registry = registry

    # ======================================================
    # UNIFIED EXECUTION GATE
    # ======================================================

    def assert_can_execute(self, target: Any = None) -> None:
        """
        Unified execution gate.

        This method supports BOTH invocation styles:

        1) Class-level lifecycle enforcement:
           ExecutionGuard.assert_can_execute(record)

        2) Instance-level phase enforcement:
           guard.assert_can_execute(record_or_dna)

        Behaviour
        ---------
        - Phase-B instance call → ExecutionNotAllowed
        - Lifecycle violation → PermissionError
        """

        # --------------------------------------------------
        # Dispatch: class-level vs instance-level
        # --------------------------------------------------

        if isinstance(self, ExecutionGuard):
            # INSTANCE CALL (Phase-aware)
            if self._registry is not None:
                raise ExecutionNotAllowed(
                    "Execution blocked: Phase-B is advisory-only"
                )

            ExecutionGuard._assert_lifecycle_allows_execution(target)
            return None

        # --------------------------------------------------
        # CLASS-LEVEL CALL (Lifecycle-only)
        # --------------------------------------------------

        ExecutionGuard._assert_lifecycle_allows_execution(self)
        return None

    # ======================================================
    # INTERNAL LIFECYCLE ENFORCEMENT
    # ======================================================

    @staticmethod
    def _assert_lifecycle_allows_execution(target: Any) -> None:
        """
        Enforce lifecycle-based execution rules only.
        """

        record = ExecutionGuard._resolve_record(target)

        state = record.state
        dna = record.dna

        # Resurrection pipeline states
        if state == "RESURRECTION_CANDIDATE":
            raise PermissionError(
                f"Execution blocked: strategy under resurrection evaluation "
                f"(dna={dna})"
            )

        if state == "REVIVAL_SHADOW":
            raise PermissionError(
                f"Execution blocked: revival shadow strategies are "
                f"observation-only (dna={dna})"
            )

        # Explicit retired state
        if state == "RETIRED":
            raise PermissionError(
                f"Execution blocked: retired strategies cannot execute "
                f"(dna={dna})"
            )

        # Any non-executable lifecycle state
        if state not in StrategyRegistry.EXECUTABLE_STATES:
            raise PermissionError(
                f"Execution blocked by lifecycle state={state} "
                f"(dna={dna})"
            )

        return None

    # ======================================================
    # RECORD RESOLUTION
    # ======================================================

    @staticmethod
    def _resolve_record(target: Any) -> StrategyRecord:
        """
        Resolve StrategyRecord from supported inputs.
        """

        if isinstance(target, StrategyRecord):
            return target

        if isinstance(target, str):
            registry = StrategyRegistry.global_instance()
            record = registry.get(target)

            if record is None:
                raise ExecutionNotAllowed(
                    f"Unknown strategy_dna: {target}"
                )

            return record

        raise ExecutionNotAllowed(
            f"Execution blocked: invalid target type "
            f"({type(target).__name__})"
        )

    # ======================================================
    # EXECUTION-TIME CAPITAL INVARIANTS
    # ======================================================

    def validate_execution(
        self,
        strategy_id: str,
        capital_fraction: float,
    ) -> None:
        """
        Validate execution-time capital invariants.

        NOTE:
        - Never called in Phase-B
        - RuntimeError is intentional (non-governance failure)
        """

        if capital_fraction <= 0.0:
            raise RuntimeError(
                f"Execution blocked: zero capital allocation "
                f"for strategy {strategy_id}"
            )

        if capital_fraction > 1.0:
            raise RuntimeError(
                f"Execution blocked: capital_fraction > 1.0 "
                f"for strategy {strategy_id}"
            )

        return None
