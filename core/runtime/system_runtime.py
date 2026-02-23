# core/runtime/system_runtime.py

from __future__ import annotations

from typing import Any

import pandas as pd

from core.regime.engine import RegimeEngine


class SystemRuntime:
    """
    Governed system runtime wrapper.

    RESPONSIBILITIES:
    - Own runtime engines
    - Delegate execution
    - Enforce environment gates
    - Bridge market data → regime detection → evidence

    MUST NOT:
    - Contain trading intelligence
    - Emit evidence directly (delegates to engines)
    - Know about red-team tests
    """

    def __init__(
        self,
        *,
        runner,
        run_registry,
        strategy_registry,
        strategy_health_store,
        capital_allocator,
        evidence_store,
        environment,
    ):
        # -------------------------
        # Core wiring
        # -------------------------
        self._runner = runner
        self._env = environment

        self._run_registry = run_registry
        self._strategy_registry = strategy_registry
        self._strategy_health_store = strategy_health_store
        self._capital_allocator = capital_allocator
        self._evidence_store = evidence_store

        # -------------------------
        # 🔑 PHASE-20 REGIME ENGINE
        # -------------------------
        # This was the missing wire.
        # RegimeEngine owns regime detection & forensic evidence.
        self._regime_engine = RegimeEngine(
            evidence_store=self._evidence_store
        )

    # ==================================================
    # EXECUTION (DELEGATED)
    # ==================================================

    def run_for(self, *args, **kwargs):
        if hasattr(self._runner, "run_for"):
            return self._runner.run_for(*args, **kwargs)
        return None

    def run_until_complete(self):
        if hasattr(self._runner, "run_until_complete"):
            return self._runner.run_until_complete()
        return None

    def reset(self):
        if hasattr(self._runner, "reset"):
            return self._runner.reset()
        return None

    def fingerprint(self):
        if hasattr(self._runner, "fingerprint"):
            return self._runner.fingerprint()
        return None

    # ==================================================
    # 🔴 PHASE-20 MARKET → REGIME BRIDGE (CRITICAL)
    # ==================================================

    def evaluate_market_tick(self, tick: Any):
        """
        Forward a single market tick into the system.

        PHASE-20 GUARANTEES:
        - Tick is observed by regime engine
        - Regime engine may emit forensic evidence
        - Runtime itself remains intelligence-free
        """

        # 1️⃣ Forward tick to execution context (if supported)
        if hasattr(self._runner, "evaluate_market_tick"):
            self._runner.evaluate_market_tick(tick)
        elif hasattr(self._runner, "inject_market_tick"):
            self._runner.inject_market_tick(tick)

        # 2️⃣ Build minimal, deterministic dataframe
        # RegimeEngine only needs price/volume semantics
        df = pd.DataFrame(
            [
                {
                    "price": getattr(tick, "price", None),
                    "volume": getattr(tick, "volume", None),
                }
            ]
        )

        # 3️⃣ Evaluate regime (THIS TRIGGERS REGIME_FLIP_DETECTED)
        self._regime_engine.evaluate(
            timeframe="INTRADAY",
            data=df,
        )

    # ==================================================
    # GOVERNANCE
    # ==================================================

    def enable_red_team(self):
        """
        Explicit governance action.
        """
        if not getattr(self._env, "allow_red_team", False):
            raise RuntimeError("Red-team access denied by environment")

        self._run_registry.enable_red_team_introspection()

    # ==================================================
    # READ-ONLY ACCESSORS
    # ==================================================

    @property
    def run_registry(self):
        return self._run_registry
