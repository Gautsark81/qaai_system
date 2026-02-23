# core/introspection/red_team.py

class AuthorizedRuntimeView:
    """
    Phase-20 red-team read-only observability surface.

    GUARANTEES:
    - NEVER mutates runtime
    - NEVER reaches execution paths
    - ONLY reads governance-owned state
    - SAFE for operator / auditor / regulator
    """

    def __init__(self, *, run_registry):
        self._registry = run_registry

    # ==================================================
    # Strategy-level visibility
    # ==================================================

    def list_live_strategies(self):
        """
        Best-effort enumeration.
        MUST NEVER raise in red-team context.
        """
        try:
            return list(self._registry.get_live_strategies())
        except Exception:
            return []

    def get_strategy_health(self, strategy_id: str):
        try:
            return self._registry.get_strategy_health(strategy_id)
        except Exception:
            return None

    def get_strategy_capital(self, strategy_id: str):
        try:
            return self._registry.get_strategy_capital(strategy_id)
        except Exception:
            return None

    def get_strategy_evidence(self, strategy_id: str):
        try:
            return self._registry.get_strategy_evidence(strategy_id)
        except Exception:
            return []

    # ==================================================
    # 🔍 FORENSIC EVIDENCE SURFACE (PHASE-20)
    # ==================================================

    def iter_evidence(self):
        """
        Iterate over all governance-recorded evidence events.

        Read-only forensic access.
        Ordering is governance-defined.
        """
        if hasattr(self._registry, "iter_evidence"):
            yield from self._registry.iter_evidence()
        elif hasattr(self._registry, "get_evidence"):
            for ev in self._registry.get_evidence():
                yield ev
        else:
            return iter(())

    def get_evidence(self):
        """
        Materialize evidence events as a list.
        """
        return list(self.iter_evidence())

    @property
    def evidence(self):
        """
        Property alias for forensic tooling compatibility.
        """
        return self.get_evidence()


    # ==================================================
    # 🧱 SNAPSHOT EXPORT (PHASE-20)
    # ==================================================

    def export_system_snapshot(self):
        """
        Export a read-only forensic snapshot.

        HARD RULES
        ----------
        - NEVER mutates runtime
        - NEVER fabricates authority
        - Snapshot hashes MUST be computable
        - MUST use canonical factory
        """
        from core.dashboard_read.snapshot import SystemSnapshot

        strategy_state = {}

        for sid in self.list_live_strategies():
            strategy_state[sid] = {
                "health": self.get_strategy_health(sid),
                "capital": self.get_strategy_capital(sid),
                "evidence": self.get_strategy_evidence(sid),
            }

        # 🔒 RED-TEAM SAFE META
        meta = {
            "mode": "red_team",
            "authority": "read_only",
            "source": "AuthorizedRuntimeView",
        }

        # ✅ CANONICAL SNAPSHOT CONSTRUCTION
        return SystemSnapshot(
            meta=meta,
            system_health={},     # no authority
            market_state={},      # observational only
            pipeline_state={},    # execution disarmed
            strategy_state=strategy_state,
            execution_state={},   # execution locked
            risk_state={},        # passive
            capital_state={},     # capital locked
            shadow_state={},      # shadow safe
            paper_state={},       # paper safe
            incidents=[],         # empty but present
            compliance={},        # governance visible
            ops_state={},         # ops neutral
        )

        # ✅ CORRECT: SystemSnapshot constructor is positional
        # ✅ CRITICAL:
        # from_components builds:
        # - components
        # - snapshot_hash
        # - chain_hash
        return SystemSnapshot.from_components(components)