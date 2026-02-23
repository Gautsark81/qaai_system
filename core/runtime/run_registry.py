# core/runtime/run_registry.py

from typing import Dict, Optional, Iterable
from datetime import timezone

from core.telemetry.emitter import TelemetryEmitter
from core.telemetry.event import TelemetryEvent
from core.telemetry.types import TelemetryCategory, TelemetrySeverity

from .run_context import RunContext
from .run_states import RunState, ALLOWED_TRANSITIONS

# Phase-20 red-team observability
from core.introspection.red_team import AuthorizedRuntimeView


class RunRegistry:
    """
    Authoritative registry for system runs.

    GUARANTEES:
    - Owns run lifecycle
    - Enforces governance invariants
    - Exposes read-only red-team observability
    """

    def __init__(
        self,
        *,
        strategy_registry=None,
        strategy_health_store=None,
        capital_allocator=None,
        evidence_store=None,
        telemetry: Optional[TelemetryEmitter] = None,
    ):
        self._runs: Dict[str, RunContext] = {}
        self._states: Dict[str, RunState] = {}
        self._telemetry = telemetry

        # Runtime-owned engines (may be None in unit tests)
        self._strategy_registry = strategy_registry
        self._strategy_health_store = strategy_health_store
        self._capital_allocator = capital_allocator
        self._evidence_store = evidence_store

        # Phase-20 red-team gate
        self._red_team_enabled = False
        self._authorized_view: Optional[AuthorizedRuntimeView] = None

    # =========================================================
    # RUN LIFECYCLE
    # =========================================================

    def register(self, ctx: RunContext) -> None:
        if ctx.run_id in self._runs:
            raise RuntimeError(f"Run {ctx.run_id} already registered")

        self._runs[ctx.run_id] = ctx
        self._states[ctx.run_id] = RunState.CREATED
        self._emit(ctx, RunState.CREATED)

    def resume(self, ctx: RunContext) -> None:
        """
        Resume an existing run with strict governance checks.
        """

        if ctx.run_id not in self._runs:
            raise RuntimeError(f"Run {ctx.run_id} not found")

        existing = self._runs[ctx.run_id]

        if existing.phase_version != ctx.phase_version:
            raise RuntimeError("Phase version mismatch on resume")

        if existing.config_fingerprint != ctx.config_fingerprint:
            raise RuntimeError("Config fingerprint mismatch on resume")

        # Resume is governance-only; no state mutation beyond ACTIVE
        self._states[ctx.run_id] = RunState.ACTIVE
        self._emit(existing, RunState.ACTIVE)

    def transition(self, run_id: str, new_state: RunState) -> None:
        if run_id not in self._states:
            raise RuntimeError(f"Run {run_id} not registered")

        current = self._states[run_id]
        if new_state not in ALLOWED_TRANSITIONS[current]:
            raise RuntimeError(f"Illegal transition {current} → {new_state}")

        self._states[run_id] = new_state
        self._emit(self._runs[run_id], new_state)

    def _emit(self, ctx: RunContext, state: RunState) -> None:
        if not self._telemetry:
            return

        event = TelemetryEvent.create(
            category=TelemetryCategory.HEARTBEAT,
            severity=TelemetrySeverity.INFO,
            run_id=ctx.run_id,
            payload={
                "state": state.value,
                "phase": ctx.phase_version,
            },
        )
        self._telemetry.emit(event)

    # =========================================================
    # 🔴 PHASE-20 RED-TEAM AUTHORIZATION
    # =========================================================

    def enable_red_team_introspection(self) -> None:
        self._red_team_enabled = True

    def _ensure_red_team_authorized(self) -> AuthorizedRuntimeView:
        if not self._red_team_enabled:
            raise RuntimeError("Red-team introspection disabled")

        if not self._runs:
            raise RuntimeError("No active runs for introspection")

        if self._authorized_view is None:
            self._authorized_view = AuthorizedRuntimeView(
                run_registry=self
            )

        return self._authorized_view

    # =========================================================
    # 🔍 FORENSIC EVIDENCE (GLOBAL)
    # =========================================================

    def iter_evidence(self) -> Iterable:
        """
        Canonical forensic evidence surface.

        Supports multiple evidence store contracts.
        """
        self._ensure_red_team_authorized()

        store = self._evidence_store
        if not store:
            return iter(())

        # 🔑 Contract adaptation (DO NOT ASSUME)
        if hasattr(store, "iter_events"):
            return store.iter_events()

        if hasattr(store, "iter_decisions"):
            return store.iter_decisions()

        if hasattr(store, "all"):
            return iter(store.all())

        if hasattr(store, "__iter__"):
            return iter(store)

        return iter(())

    # =========================================================
    # 🔍 STRATEGY-LEVEL READ-ONLY ACCESS
    # =========================================================

    def get_live_strategies(self):
        self._ensure_red_team_authorized()
        return (
            self._strategy_registry.list_live_strategies()
            if self._strategy_registry
            else []
        )

    def get_strategy_health(self, strategy_id: str):
        self._ensure_red_team_authorized()
        return (
            self._strategy_health_store.get_health(strategy_id)
            if self._strategy_health_store
            else None
        )

    def get_strategy_capital(self, strategy_id: str):
        self._ensure_red_team_authorized()
        return (
            self._capital_allocator.get_allocated_capital(strategy_id)
            if self._capital_allocator
            else None
        )

    def get_strategy_evidence(self, strategy_id: str):
        self._ensure_red_team_authorized()
        if not self._evidence_store:
            return []
        if hasattr(self._evidence_store, "by_strategy"):
            return self._evidence_store.by_strategy(strategy_id)
        return []
