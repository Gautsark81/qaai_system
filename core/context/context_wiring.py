# core/context/context_wiring.py

from types import MappingProxyType

from core.regime.regime_context import RegimeContext
from core.regime.context_contracts import (
    StrategyContextView,
    MetaModelContextView,
    ObservabilityContextView,
)

from core.context.context_lineage import ContextLineage
from core.context.context_governance import GovernanceNotes
from core.context.context_capital_risk import (
    build_capital_view,
    build_risk_view,
)
from core.context.context_visibility import ReadOnlyDict


# ─────────────────────────────────────────────
# Phase-6.1 — Risk Explanation
# ─────────────────────────────────────────────

def _build_risk_explanation(*, risk_view: dict, regime):
    """
    Explanatory-only risk rationale.
    Deterministic.
    No execution authority.
    """
    explanation = {
        "summary": (
            f"Risk regime assessed as {risk_view['risk_regime']} "
            f"under {regime.value if hasattr(regime, 'value') else regime}."
        ),
        "drivers": [
            f"Market regime: {regime.value if hasattr(regime, 'value') else regime}",
            f"Risk band: {risk_view['risk_regime']}",
        ],
        "assumptions": [
            "Regime classification is stable",
            "No external shock detected",
        ],
        "confidence": risk_view["confidence"],
        "derived_from": "risk_view",
    }

    return ReadOnlyDict(explanation)


# ─────────────────────────────────────────────
# Phase-6.2 / 6.3 — Strategy Risk Signals
# ─────────────────────────────────────────────

def _build_strategy_risk_signals(*, risk_view: dict):
    """
    Strategy-facing advisory signals.
    MUST NOT influence execution.
    """
    signals = {
        "risk_level": risk_view["risk_regime"],
        "confidence": risk_view["confidence"],
        "advisory": True,
        "source": "risk_view",
    }

    return ReadOnlyDict(signals)


# ─────────────────────────────────────────────
# Phase-7.0 — Capital Advisory (NEW)
# ─────────────────────────────────────────────

def _build_capital_advisory(*, capital_view: dict):
    """
    Phase-7.0 — Capital Advisory

    Advisory-only.
    Deterministic.
    NO execution authority.
    """

    band = capital_view["utilization_band"]

    if band == "LOW":
        exposure = "LOW"
        rationale = "Capital utilization is low — exposure should be reduced."
    elif band == "NORMAL":
        exposure = "NORMAL"
        rationale = "Capital utilization is within normal operating range."
    elif band == "HIGH":
        exposure = "REDUCED"
        rationale = "Capital utilization elevated — reduce new exposure."
    else:
        exposure = "BLOCK"
        rationale = "Capital utilization unsafe — block new exposure."

    advisory = {
        "recommended_exposure": exposure,
        "confidence": capital_view["confidence"],
        "rationale": rationale,
        "constraints": [
            "Advisory only",
            "No execution authority",
            "No capital override",
        ],
        "source": "capital_view",
    }

    return ReadOnlyDict(advisory)

# ─────────────────────────────────────────────
# Base Provider
# ─────────────────────────────────────────────

class _BaseContextProvider:
    """
    Internal base class.
    Enforces one-way, read-only context exposure.
    """

    __slots__ = ("_view",)

    def __init__(self, view):
        self._view = view

    def get(self, symbol: str):
        """
        Return an immutable, enriched context snapshot.
        """

        snapshot = self._view.snapshot(symbol)
        if snapshot is None:
            return None

        enriched = dict(snapshot)

        # ─────────────────────────────────────────
        # Phase-5.3 — Context Lineage (LOCKED)
        # ─────────────────────────────────────────
        source = "RegimeMemory"
        base_context = getattr(self._view, "_base_context", None)

        detector_ids = []
        if base_context is not None and hasattr(base_context, "_memory"):
            events = base_context._memory._events.get(symbol, [])
            if events:
                detector_ids = [events[-1].detector_id]

        regimes = [enriched.get("current_regime")]

        lineage = ContextLineage(
            symbol=symbol,
            source=source,
            detector_ids=detector_ids,
            regimes=regimes,
            snapshot_hash=ContextLineage.compute_hash(
                symbol=symbol,
                source=source,
                detector_ids=detector_ids,
                regimes=regimes,
            ),
        )

        enriched["lineage"] = lineage

        # ─────────────────────────────────────────
        # Phase-5.4 — Governance Notes (LOCKED)
        # ─────────────────────────────────────────
        enriched["governance_notes"] = GovernanceNotes(
            context_hash=lineage.snapshot_hash
        )

        # ─────────────────────────────────────────
        # Phase-6.0 — Capital & Risk Views (LOCKED)
        # ─────────────────────────────────────────
        capital_view = build_capital_view(enriched)
        risk_view = build_risk_view(enriched)

        enriched["capital_view"] = capital_view
        enriched["risk_view"] = risk_view

        # ─────────────────────────────────────────
        # Phase-6.1 — Risk Explanation (LOCKED)
        # ─────────────────────────────────────────
        enriched["risk_explanation"] = _build_risk_explanation(
            risk_view=risk_view,
            regime=enriched.get("current_regime"),
        )

        # ─────────────────────────────────────────
        # Phase-6.2 / 6.3 — Strategy Risk Signals
        # ─────────────────────────────────────────
        enriched["risk_signals"] = _build_strategy_risk_signals(
            risk_view=risk_view
        )

        # ─────────────────────────────────────────
        # Phase-7.0 — Capital Advisory (NEW)
        # ─────────────────────────────────────────
        enriched["capital_advisory"] = _build_capital_advisory(
            capital_view=capital_view
        )

        # FINAL FREEZE
        return MappingProxyType(enriched)


# ─────────────────────────────────────────────
# Context Providers
# ─────────────────────────────────────────────

class StrategyContextProvider(_BaseContextProvider):
    """Strategy-facing advisory context."""

    def __init__(self, base_context: RegimeContext):
        view = StrategyContextView(base_context)
        view._base_context = base_context
        super().__init__(view)


class MetaModelContextProvider(_BaseContextProvider):
    """Meta-model context provider."""

    def __init__(self, base_context: RegimeContext):
        view = MetaModelContextView(base_context)
        view._base_context = base_context
        super().__init__(view)


class ObservabilityContextProvider(_BaseContextProvider):
    """Audit / dashboard context provider."""

    def __init__(self, base_context: RegimeContext):
        view = ObservabilityContextView(base_context)
        view._base_context = base_context
        super().__init__(view)
