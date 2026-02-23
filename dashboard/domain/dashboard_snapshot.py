from dataclasses import dataclass
from typing import Any, Optional, Dict
from types import MappingProxyType
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import hashlib
import copy
import json


from dashboard.domain.snapshot_hash import compute_snapshot_hash


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

class _FrozenDict(dict):
    """Dict that raises FrozenInstanceError on mutation."""
    def __setitem__(self, key, value):
        raise FrozenInstanceError("cannot assign to field")

    def update(self, *args, **kwargs):
        raise FrozenInstanceError("cannot assign to field")

    def pop(self, *args, **kwargs):
        raise FrozenInstanceError("cannot assign to field")

    def clear(self):
        raise FrozenInstanceError("cannot assign to field")

    def __deepcopy__(self, memo):
        return self


def _deep_freeze(obj):
    if isinstance(obj, dict):
        return MappingProxyType({k: _deep_freeze(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return tuple(_deep_freeze(v) for v in obj)
    return obj


def _safe_copy(obj):
    """
    Phase-8 critical helper.

    mappingproxy → dict
    tuple/list/dict → recursively safe copied
    immutable primitives → returned as-is
    """
    if isinstance(obj, MappingProxyType):
        return {k: _safe_copy(v) for k, v in obj.items()}
    if isinstance(obj, dict):
        return {k: _safe_copy(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_safe_copy(v) for v in obj)
    try:
        return copy.deepcopy(obj)
    except TypeError:
        return obj


def _chain_hash(
    *,
    core_hash: str,
    parent_hash: Optional[str],
    lineage_depth: int,
    cause: str,
) -> str:
    h = hashlib.sha256()
    h.update(core_hash.encode())
    h.update((parent_hash or "").encode())
    h.update(str(lineage_depth).encode())
    h.update(cause.encode())
    return h.hexdigest()


# ─────────────────────────────────────────────
# Phase-2.2 Governance Record (RECORD-ONLY)
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class _GovernanceDecision:
    snapshot_hash: str
    status: str
    reason: str
    severity: str
    recorded_at: datetime
    is_binding: bool = False


# ─────────────────────────────────────────────
# Phase-2.3 Operator Acknowledgement Record
# ─────────────────────────────────────────────

_ALLOWED_OPERATOR_EVENTS = {
    "ALERT_ACK",
    "REVIEW_CONFIRMED",
    "DEFERRED_DECISION",
    "ESCALATION_MISSED",
}


@dataclass(frozen=True)
class _OperatorAcknowledgement:
    snapshot_hash: str
    event_type: str
    context: str
    recorded_at: datetime
    is_binding: bool = False


# ─────────────────────────────────────────────
# Snapshot
# ─────────────────────────────────────────────

@dataclass
class DashboardSnapshot:
    """
    Immutable dashboard snapshot.
    Phase-1.4 → Phase-3.0 compliant.
    """

    # Core (hashed)
    core: dict

    # Derived (not hashed)
    system_mood_detail: Any
    system_mood_drift: Any
    violation_pulse: Any

    # Lineage
    parent_hash: Optional[str] = None
    lineage_depth: int = 0
    cause: str = "BOOT"

    # Governance (Phase-1.7)
    governance_status: str = "UNCHECKED"
    governance_reason: Optional[str] = None
    governance_checked_at: Optional[datetime] = None

    # Execution arming (Phase-1.9)
    execution_armed: bool = False
    execution_arming_reason: Optional[str] = None
    execution_arming_checked_at: Optional[datetime] = None

    # ─────────────────────────────────────────────

    def __post_init__(self):
        core_hash = compute_snapshot_hash(self.core)

        snapshot_hash = _chain_hash(
            core_hash=core_hash,
            parent_hash=self.parent_hash,
            lineage_depth=self.lineage_depth,
            cause=self.cause,
        )

        object.__setattr__(self, "core", _deep_freeze(self.core))
        object.__setattr__(self, "_hash", snapshot_hash)
        object.__setattr__(self, "_sealed", True)

    # ─────────────────────────────────────────────
    # Immutability Contract (CRITICAL)
    # ─────────────────────────────────────────────

    def __setattr__(self, key, value):
        if "_sealed" in self.__dict__:
            if key in {
                "hash",
                "hash_algo",
                "governance_status",
                "governance_reason",
                "governance_checked_at",
                "execution_armed",
                "execution_arming_reason",
                "execution_arming_checked_at",
            }:
                raise FrozenInstanceError("cannot assign to field")

            raise TypeError("DashboardSnapshot is immutable")

        object.__setattr__(self, key, value)

    def __getattr__(self, item: str):
        core = self.__dict__.get("core")
        if core is not None and item in core:
            return core[item]
        raise AttributeError(item)

    # ─────────────────────────────────────────────
    # Public Properties
    # ─────────────────────────────────────────────

    @property
    def system_mood(self) -> float:
        return float(self.system_mood_detail.mood)

    @property
    def hash(self) -> str:
        return self._hash

    @property
    def hash_algo(self) -> str:
        return "sha256"

    # ─────────────────────────────────────────────
    # Phase-8.1 — Operator Read-Only Surface
    # ─────────────────────────────────────────────

    @property
    def operator(self) -> Dict[str, Any]:
        """
        READ-ONLY · SNAPSHOT-ANCHORED · OBSERVATIONAL ONLY
        """

        view = {
            "system": self.core.get("system"),
            "market": self.core.get("market"),
            "strategies": self.core.get("strategies"),
            "capital": self.core.get("capital"),
            "execution": self.core.get("execution"),
            "governance": self.core.get("governance"),
            "interpretation": getattr(self, "interpretation", None),
            "meta": self.core.get("meta"),
        }

        safe = {
            k: _safe_copy(v)
            for k, v in view.items()
            if v is not None
        }

        return _FrozenDict(safe)

    # ─────────────────────────────────────────────
    # Phase-8.2 — Operator Audit Surface (NEW)
    # ─────────────────────────────────────────────

    @property
    def operator_audit(self) -> Dict[str, Any]:
        """
        Phase-8.2 Operator Audit Surface

        READ-ONLY
        Deterministic
        Snapshot-anchored
        Forensic (includes operator-view checksum)
        Non-binding
        """

        # Reuse Phase-8.1 operator view
        operator_view = self.operator

        # Deterministic checksum of operator-visible data
        operator_view_hash = hashlib.sha256(
            json.dumps(
                dict(operator_view),
                sort_keys=True,
                default=str,
            ).encode()
        ).hexdigest()

        audit = {
            "snapshot_hash": self.hash,
            "hash_algo": self.hash_algo,
            "parent_hash": self.parent_hash,
            "lineage_depth": self.lineage_depth,
            "cause": self.cause,

            # Forensic linkage
            "operator_view_hash": operator_view_hash,

            # Governance / authority flags
            "is_advisory": True,
            "can_trigger_actions": False,
        }

        return _FrozenDict(audit)


    # ─────────────────────────────────────────────
    # Phase-8.3 — Audit Lineage Surface (NEW)
    # ─────────────────────────────────────────────

    @property
    def audit_lineage(self) -> Dict[str, Any]:
        """
        Phase-8.3 Audit Lineage Surface

        READ-ONLY
        Deterministic
        Snapshot-anchored
        Promotion-aware
        Cryptographically bound
        Non-binding
        """

        # Operator surfaces (already deterministic)
        operator_view = self.operator
        operator_audit = self.operator_audit

        operator_view_hash = operator_audit["operator_view_hash"]

        operator_audit_hash = hashlib.sha256(
            json.dumps(
                dict(operator_audit),
                sort_keys=True,
                default=str,
            ).encode()
        ).hexdigest()

        lineage = {
            # Snapshot identity
            "snapshot_hash": self.hash,
            "hash_algo": self.hash_algo,

            # Lineage chain
            "parent_hash": self.parent_hash,
            "lineage_depth": self.lineage_depth,
            "cause": self.cause,

            # Cryptographic bindings
            "operator_view_hash": operator_view_hash,
            "operator_audit_hash": operator_audit_hash,

            # Authority flags
            "is_advisory": True,
            "can_trigger_actions": False,
        }

        return _FrozenDict(lineage)

    # ─────────────────────────────────────────────
    # Phase-8.4 — Forensic Replay Surface (NEW)
    # ─────────────────────────────────────────────

    @property
    def forensic_replay(self) -> Dict[str, Any]:
        """
        Phase-8.4 Forensic Replay Surface

        READ-ONLY
        Deterministic
        Snapshot-anchored
        Full operator reconstruction
        Non-binding
        """

        replay = {
            # Snapshot identity
            "snapshot_hash": self.hash,
            "hash_algo": self.hash_algo,
            "parent_hash": self.parent_hash,
            "lineage_depth": self.lineage_depth,
            "cause": self.cause,

            # Reconstructed views
            "operator_view": _safe_copy(dict(self.operator)),
            "operator_audit": _safe_copy(dict(self.operator_audit)),
            "audit_lineage": _safe_copy(dict(self.audit_lineage)),

            # Authority flags
            "is_advisory": True,
            "can_trigger_actions": False,
        }

        return _FrozenDict(replay)

    # ─────────────────────────────────────────────
    # Phase-2.4 — Decision Drift Analytics
    # ─────────────────────────────────────────────

    @property
    def decision_drift_metrics(self) -> Dict[str, Any]:
        return _FrozenDict({
            "alert_fatigue_index": 0.0,
            "repeated_approval_rate": 0.0,
            "contradiction_rate": 0.0,
            "decision_latency_variance": 0.0,
            "derived_from": self.hash,
            "timestamp": datetime.now(timezone.utc),
            "is_advisory": True,
            "can_trigger_actions": False,
        })

    # ─────────────────────────────────────────────
    # Phase-3.0 — Adaptive Context (READ-ONLY)
    # ─────────────────────────────────────────────

    @property
    def adaptive_context(self) -> Dict[str, Any]:
        return _FrozenDict({
            "market_regime": "UNKNOWN",
            "volatility_climate": "UNKNOWN",
            "liquidity_stress": "UNKNOWN",
            "strategy_interaction_pressure": "UNKNOWN",
            "confidence": 0.4,
            "uncertainty_note": (
                "Adaptive context is descriptive only and must never "
                "be used for execution, capital, or governance decisions."
            ),
            "derived_from": self.hash,
            "timestamp": datetime.now(timezone.utc),
            "is_advisory": True,
            "can_trigger_actions": False,
        })

    # ─────────────────────────────────────────────
    # Phase-2 Record APIs (RECORD-ONLY)
    # ─────────────────────────────────────────────

    def record_governance_decision(self, *, status: str, reason: str, severity: str):
        if status not in {"APPROVE", "REJECT", "HOLD"}:
            raise ValueError("Invalid governance decision status")
        if not reason or not reason.strip():
            raise ValueError("Governance decision requires a reason")
        if severity not in {"LOW", "MEDIUM", "HIGH"}:
            raise ValueError("Invalid governance severity")

        return _GovernanceDecision(
            snapshot_hash=self.hash,
            status=status,
            reason=reason,
            severity=severity,
            recorded_at=datetime.now(timezone.utc),
        )

    def record_operator_acknowledgement(self, *, event_type: str, context: str):
        if event_type not in _ALLOWED_OPERATOR_EVENTS:
            raise ValueError("Invalid operator acknowledgement event type")
        if not context or not context.strip():
            raise ValueError("Operator acknowledgement requires context")

        return _OperatorAcknowledgement(
            snapshot_hash=self.hash,
            event_type=event_type,
            context=context,
            recorded_at=datetime.now(timezone.utc),
        )

    # ─────────────────────────────────────────────
    # Promotion & Governance / Execution
    # ─────────────────────────────────────────────

    def promote(self, *, cause: str) -> "DashboardSnapshot":
        return DashboardSnapshot(
            core=self.core,
            system_mood_detail=self.system_mood_detail,
            system_mood_drift=self.system_mood_drift,
            violation_pulse=self.violation_pulse,
            parent_hash=self.hash,
            lineage_depth=self.lineage_depth + 1,
            cause=cause,
            governance_status=self.governance_status,
            governance_reason=self.governance_reason,
            governance_checked_at=self.governance_checked_at,
            execution_armed=self.execution_armed,
            execution_arming_reason=self.execution_arming_reason,
            execution_arming_checked_at=self.execution_arming_checked_at,
        )

    def evaluate_governance(self, *, status: str, reason: str) -> "DashboardSnapshot":
        if status not in {"APPROVED", "REJECTED"}:
            raise ValueError("Invalid governance status")
        if not reason or not reason.strip():
            raise ValueError("Governance evaluation requires a reason")

        return DashboardSnapshot(
            core=self.core,
            system_mood_detail=self.system_mood_detail,
            system_mood_drift=self.system_mood_drift,
            violation_pulse=self.violation_pulse,
            parent_hash=self.hash,
            lineage_depth=self.lineage_depth + 1,
            cause="GOVERNANCE_EVALUATION",
            governance_status=status,
            governance_reason=reason,
            governance_checked_at=datetime.now(timezone.utc),
            execution_armed=self.execution_armed,
            execution_arming_reason=self.execution_arming_reason,
            execution_arming_checked_at=self.execution_arming_checked_at,
        )

    def arm_execution(self, *, approved: bool, reason: str) -> "DashboardSnapshot":
        if not reason or not reason.strip():
            raise ValueError("Execution arming requires a non-empty reason")

        return DashboardSnapshot(
            core=self.core,
            system_mood_detail=self.system_mood_detail,
            system_mood_drift=self.system_mood_drift,
            violation_pulse=self.violation_pulse,
            parent_hash=self.hash,
            lineage_depth=self.lineage_depth + 1,
            cause="EXECUTION_ARMING",
            governance_status=self.governance_status,
            governance_reason=self.governance_reason,
            governance_checked_at=self.governance_checked_at,
            execution_armed=bool(approved),
            execution_arming_reason=reason,
            execution_arming_checked_at=datetime.now(timezone.utc),
        )

    # ─────────────────────────────────────────────
    # Deepcopy Safety (Phase-8 Critical)
    # ─────────────────────────────────────────────

    def __deepcopy__(self, memo):
        clone = DashboardSnapshot(
            core=_safe_copy(dict(self.core)),
            system_mood_detail=copy.deepcopy(self.system_mood_detail, memo),
            system_mood_drift=copy.deepcopy(self.system_mood_drift, memo),
            violation_pulse=copy.deepcopy(self.violation_pulse, memo),
            parent_hash=self.parent_hash,
            lineage_depth=self.lineage_depth,
            cause=self.cause,
            governance_status=self.governance_status,
            governance_reason=self.governance_reason,
            governance_checked_at=self.governance_checked_at,
            execution_armed=self.execution_armed,
            execution_arming_reason=self.execution_arming_reason,
            execution_arming_checked_at=self.execution_arming_checked_at,
        )
        if hasattr(self, "interpretation"):
            object.__setattr__(
                clone,
                "interpretation",
                copy.deepcopy(self.interpretation, memo),
            )
        return clone
