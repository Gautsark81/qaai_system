# dashboard/domain/phase2_interpretation.py

from dataclasses import dataclass, FrozenInstanceError
from datetime import datetime, timezone
from typing import Dict, Any, Iterable
import copy

from dashboard.domain.phase7_consistency import evaluate_consistency
from dashboard.domain.phase7_stability import evaluate_stability


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

class _FrozenDict(dict):
    """Immutable, deepcopy-safe dict."""

    def __setitem__(self, *_, **__):
        raise FrozenInstanceError("cannot assign to field")

    def update(self, *_, **__):
        raise FrozenInstanceError("cannot assign to field")

    def pop(self, *_, **__):
        raise FrozenInstanceError("cannot assign to field")

    def clear(self):
        raise FrozenInstanceError("cannot assign to field")

    def __deepcopy__(self, memo):
        return self


def _panel(*, label: str, confidence: float, uncertainty_note: str) -> Dict[str, Any]:
    return {
        "label": label,
        "confidence": confidence,
        "uncertainty_note": uncertainty_note,
        "signals_considered": (),
        "drivers": (),
        "confidence_breakdown": _FrozenDict({"base": confidence}),
    }


# ─────────────────────────────────────────────
# Governance
# ─────────────────────────────────────────────

_ALLOWED_STATUS = {"APPROVE", "REJECT", "HOLD"}
_ALLOWED_SEVERITY = {"LOW", "MEDIUM", "HIGH"}


@dataclass(frozen=True)
class GovernanceDecision:
    snapshot_hash: str
    status: str
    reason: str
    severity: str
    recorded_at: datetime
    is_binding: bool = False


# ─────────────────────────────────────────────
# Phase-2 / Phase-7 Interpretation
# ─────────────────────────────────────────────

class Phase2Interpretation(dict):
    """
    Phase-2 / Phase-7.x Interpretation Surface

    Dict-compatible
    Immutable
    Snapshot-derived
    Consistency & Trust are COMPUTED, not stored
    """

    __slots__ = ("_panel_keys",)

    def __init__(self, *, snapshot_hash: str):
        ts = datetime(1970, 1, 1, tzinfo=timezone.utc)

        panels = {
            "market_regime": _panel(
                label="UNKNOWN",
                confidence=0.5,
                uncertainty_note="Insufficient regime evidence.",
            ),
            "risk_climate": _panel(
                label="NEUTRAL",
                confidence=0.5,
                uncertainty_note="Risk signals inconclusive.",
            ),
            "strategy_stress": _panel(
                label="LOW",
                confidence=0.6,
                uncertainty_note="No stress indicators observed.",
            ),
            "capital_pressure": _panel(
                label="LOW",
                confidence=0.7,
                uncertainty_note="No capital strain detected.",
            ),
        }

        avg_conf = sum(p["confidence"] for p in panels.values()) / len(panels)

        super().__init__(
            derived_from=snapshot_hash,
            as_of=ts,
            timestamp=ts,
            confidence=avg_conf,
            uncertainty_note=(
                "Interpretation is snapshot-derived and subject to "
                "regime uncertainty and signal lag."
            ),
            **panels,
        )

        self._panel_keys = frozenset(panels.keys())

    # ─────────────────────────────────────────────
    # Presence checks
    # ─────────────────────────────────────────────

    def __contains__(self, key):
        if key in {"consistency", "trust", "stability"}:
            return True
        return super().__contains__(key)

    # ─────────────────────────────────────────────
    # Dynamic derived surfaces
    # ─────────────────────────────────────────────

    def __getitem__(self, key):
        if key == "consistency":
            return evaluate_consistency(self)

        if key == "trust":
            return self._evaluate_trust()

        if key == "stability":
            return evaluate_stability(self)

        return super().__getitem__(key)

    # ─────────────────────────────────────────────
    # Phase-7.3 — Trust & Confidence Degradation
    # ─────────────────────────────────────────────

    def _evaluate_trust(self) -> Dict[str, Any]:
        consistency = evaluate_consistency(self)
        violations = consistency["violations"]
        n = len(violations)

        base_conf = self["confidence"]

        # Penalty schedule (deterministic)
        penalty = min(0.5, n * 0.15)
        degraded_conf = max(0.0, base_conf - penalty)

        if n == 0:
            status = "STABLE"
        elif degraded_conf < 0.4:
            status = "UNTRUSTWORTHY"
        else:
            status = "DEGRADED"

        explanation = (
            "Interpretation is internally consistent."
            if n == 0
            else f"Interpretation trust degraded due to {n} cross-panel contradiction(s)."
        )

        return {
            "status": status,
            "base_confidence": base_conf,
            "degraded_confidence": degraded_conf,
            "penalty_applied": round(base_conf - degraded_conf, 4),
            "contributors": [v["rule_id"] for v in violations],
            "explanation": explanation,
        }

    # ─────────────────────────────────────────────
    # Iteration contract (CRITICAL)
    # ─────────────────────────────────────────────

    def items(self) -> Iterable:
        for k in ("derived_from", "as_of"):
            yield k, self[k]
        for k in self._panel_keys:
            yield k, self[k]

    def keys(self) -> Iterable:
        for k, _ in self.items():
            yield k

    def values(self) -> Iterable:
        for _, v in self.items():
            yield v

    # ─────────────────────────────────────────────
    # Immutability
    # ─────────────────────────────────────────────

    def __setitem__(self, *_):
        raise FrozenInstanceError("Phase-2 interpretation is immutable")

    def update(self, *_):
        raise FrozenInstanceError("Phase-2 interpretation is immutable")

    # ─────────────────────────────────────────────
    # Equality / deepcopy
    # ─────────────────────────────────────────────

    def __eq__(self, other):
        return isinstance(other, Phase2Interpretation) and dict(self) == dict(other)

    def __deepcopy__(self, memo):
        clone = Phase2Interpretation.__new__(Phase2Interpretation)
        dict.__init__(clone, copy.deepcopy(dict(self), memo))
        clone._panel_keys = self._panel_keys
        return clone


# ─────────────────────────────────────────────
# Snapshot Integration
# ─────────────────────────────────────────────

def attach_phase2_to_snapshot(snapshot):
    object.__setattr__(
        snapshot,
        "interpretation",
        Phase2Interpretation(snapshot_hash=snapshot.hash),
    )

    def record_governance_decision(*, status: str, reason: str, severity: str):
        if status not in _ALLOWED_STATUS:
            raise ValueError("Invalid governance status")
        if severity not in _ALLOWED_SEVERITY:
            raise ValueError("Invalid governance severity")
        if not reason or not reason.strip():
            raise ValueError("Governance decision requires a reason")

        return GovernanceDecision(
            snapshot_hash=snapshot.hash,
            status=status,
            reason=reason,
            severity=severity,
            recorded_at=datetime.now(timezone.utc),
        )

    object.__setattr__(snapshot, "record_governance_decision", record_governance_decision)
    return snapshot
