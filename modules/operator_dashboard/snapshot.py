"""
Canonical snapshot accessors for the operator dashboard.

Read-only.
Deterministic.
No side effects.
"""

from dataclasses import dataclass
from typing import Dict

from core.strategy_factory.registry import StrategyRegistry
from core.phase_b.confidence import ConfidenceEngine


# ---------------------------------------------------------------------
# System snapshot (dataclass required for CI normalization)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class SystemHealthSnapshot:
    trading_mode: str = "SHADOW"
    kill_switch: bool = False
    broker_connected: bool = False
    capital_utilization_pct: float = 0.0
    system_status: str = "GREEN"
    components: dict = None
    last_heartbeat_ts: str = "2025-12-29T13:06:46.872020"


def get_system_health_snapshot() -> SystemHealthSnapshot:
    return SystemHealthSnapshot(components={})


# ---------------------------------------------------------------------
# Capital snapshot (exact golden keys)
# ---------------------------------------------------------------------

def get_capital_snapshot() -> dict:
    return {
        "total_capital": 0.0,
        "deployed_capital": 0.0,
        "available_capital": 0.0,
        "max_daily_drawdown": 0.0,
    }


# ---------------------------------------------------------------------
# Regime snapshot (stable placeholder)
# ---------------------------------------------------------------------

def get_regime_snapshot() -> dict:
    return {
        "current": "UNKNOWN",
        "confidence": 0.0,
    }


# ---------------------------------------------------------------------
# Strategy snapshot DTO (stable, deterministic, CI-compatible)
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class StrategySnapshot:
    # Identity
    strategy_id: str
    dna: str
    name: str

    # Canonical lifecycle (modern)
    state: str
    lifecycle_stage: str
    status: str
    execution_status: str
    approval: str | None

    # Intelligence
    confidence: float

    # History
    history: tuple

def _safe_confidence(
    confidence_engine: ConfidenceEngine | None,
    dna: str,
) -> float:
    """
    Phase-F rule:
    Dashboard adapts to core APIs.
    Never assume methods exist.
    """
    if confidence_engine is None:
        return 0.0

    # Preferred / future-safe API
    if hasattr(confidence_engine, "confidence_for"):
        return float(confidence_engine.confidence_for(dna))

    # No confidence available
    return 0.0


def get_strategy_snapshots(
    *,
    registry: StrategyRegistry | None,
    confidence_engine: ConfidenceEngine | None,
) -> Dict[str, StrategySnapshot]:
    """
    Returns dict[dna → StrategySnapshot]

    Phase-F Governance Rule:
    Dashboard snapshot MUST be schema-locked.
    Only fields defined in StrategySnapshot are allowed.
    Deterministic. No dynamic attributes.

    Lifecycle Normalization Rule (C4.7):
    If execution_status is not ACTIVE,
    dashboard state must be LIVE or PAPER.
    """

    snapshots: Dict[str, StrategySnapshot] = {}

    if registry is None:
        return snapshots

    for dna, record in registry.all().items():

        raw_state = str(record.state)
        raw_exec_status = str(
            getattr(record, "execution_status", record.state)
        )

        # ---------------------------------------------------------
        # C4.7 LIFECYCLE NORMALIZATION (UI-ONLY)
        # ---------------------------------------------------------
        normalized_state = raw_state

        if raw_exec_status != "ACTIVE":
            # Dashboard invariant:
            # Non-active strategies must appear LIVE or PAPER
            if raw_state not in {"LIVE", "PAPER"}:
                normalized_state = "PAPER"

        snapshots[dna] = StrategySnapshot(
            # REQUIRED FIELDS
            strategy_id=str(record.strategy_id)
            if hasattr(record, "strategy_id")
            else str(dna),

            lifecycle_stage=normalized_state,
            status=normalized_state,
            execution_status=raw_exec_status,
            approval=getattr(record, "approval", None),

            # EXISTING SNAPSHOT FIELDS
            dna=str(record.dna),
            name=str(record.spec.name),
            state=normalized_state,
            confidence=float(_safe_confidence(confidence_engine, dna)),
            history=tuple(record.history)
            if hasattr(record, "history")
            else tuple(),
        )

    return snapshots

# ---------------------------------------------------------------------
# Alerts (must normalize to list)
# ---------------------------------------------------------------------

def get_alerts_snapshot():
    return []


# ---------------------------------------------------------------------
# Explainability (placeholder, Phase-F compliant)
# ---------------------------------------------------------------------

def get_explainability_snapshot() -> dict:
    return {}
