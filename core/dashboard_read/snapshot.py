from __future__ import annotations

from dataclasses import dataclass, field, asdict, fields, is_dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Type, get_origin, get_args
import uuid
import json
import hashlib

from core.dashboard_read.fingerprint import compute_snapshot_fingerprint

# =====================================================================
# UTILITIES
# =====================================================================

def _filter_fields(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
    allowed = {f.name for f in fields(cls)}
    return {k: v for k, v in payload.items() if k in allowed}


def _dt_to_str(dt: datetime) -> str:
    return dt.isoformat()


def _str_to_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _canonical_json(payload: Dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _safe_asdict(obj: Any) -> Any:
    if is_dataclass(obj):
        return {k: _safe_asdict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [_safe_asdict(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _safe_asdict(v) for k, v in obj.items()}
    return obj


def _rehydrate(cls: Type, payload: Any, *, allow_empty: bool = False):
    """
    Deterministic deep rehydration of dataclasses.
    Guarantees equality on JSON round-trip.
    Adversarial-safe: malformed payloads degrade, never crash.
    """
    from typing import Union, get_type_hints
    from dataclasses import MISSING

    # Non-dataclass targets are passthrough
    if not is_dataclass(cls):
        return payload

    # Explicit degraded / empty state
    if allow_empty and (payload == {} or payload == [] or payload is None):
        return {}

    # Malformed payload → degrade safely
    if not isinstance(payload, dict):
        return {}

    # 🔑 CRITICAL FIX: resolve real runtime types
    resolved_types = get_type_hints(cls)

    kwargs = {}
    for f in fields(cls):
        t = resolved_types.get(f.name, f.type)
        origin = get_origin(t)

        # unwrap Optional[T] (Union[T, None])
        if origin is Union:
            args = [a for a in get_args(t) if a is not type(None)]
            if len(args) == 1:
                t = args[0]
                origin = get_origin(t)

        if f.name in payload:
            value = payload[f.name]

            # nested dataclass
            if is_dataclass(t):
                kwargs[f.name] = _rehydrate(t, value, allow_empty=allow_empty)

            # list[T]
            elif origin is list:
                inner = get_args(t)[0]
                if isinstance(value, list):
                    if is_dataclass(inner):
                        kwargs[f.name] = [
                            _rehydrate(inner, v, allow_empty=allow_empty)
                            for v in value
                        ]
                    else:
                        kwargs[f.name] = list(value)
                else:
                    kwargs[f.name] = []

            # primitive / mapping
            else:
                kwargs[f.name] = value

        else:
            # deterministic fill for missing fields
            if f.default is not MISSING:
                kwargs[f.name] = f.default
            elif f.default_factory is not MISSING:  # type: ignore
                kwargs[f.name] = f.default_factory()  # type: ignore
            else:
                kwargs[f.name] = None

    return cls(**kwargs)

# =====================================================================
# SNAPSHOT META
# =====================================================================

@dataclass(frozen=True)
class SnapshotMeta:
    snapshot_id: str
    created_at: datetime

    execution_mode: str
    market_status: str
    system_version: str

    failures: Dict[str, str] = field(default_factory=dict)
    failure_count: int = 0
    is_degraded: bool = False

    schema_version: int = 1
    fingerprint: str = ""
    payload_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = _dt_to_str(self.created_at)
        return d

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SnapshotMeta":
        data = dict(payload)
        data["created_at"] = _str_to_dt(data["created_at"])
        data.setdefault("snapshot_id", f"SNAPSHOT_{uuid.uuid4().hex}")
        data.setdefault("schema_version", 1)
        data.setdefault("fingerprint", "")
        data.setdefault("payload_hash", "")
        return cls(**_filter_fields(cls, data))

# =====================================================================
# STATE MODELS
# =====================================================================

@dataclass(frozen=True)
class DataFeedHealth:
    provider: str
    status: str
    latency_ms: Optional[int]


@dataclass(frozen=True)
class BrokerHealth:
    connected: bool
    rate_limit_state: str
    last_error: Optional[str]


@dataclass(frozen=True)
class SystemHealth:
    data_feeds: List[DataFeedHealth]
    broker: BrokerHealth
    services: Dict[str, str]
    alerts_active: bool


@dataclass(frozen=True)
class MarketRegime:
    volatility: str
    liquidity: str
    stress_level: str


@dataclass(frozen=True)
class ExtremeEventState:
    active: bool
    classification: Optional[str]


@dataclass(frozen=True)
class MarketState:
    regime: MarketRegime
    extreme_event: ExtremeEventState
    session: str


@dataclass(frozen=True)
class ScreeningState:
    symbols_seen: int
    passed: int
    rejected_by_reason: Dict[str, int]


@dataclass(frozen=True)
class WatchlistState:
    added: int
    removed: int
    active: int


@dataclass(frozen=True)
class StrategyFactoryState:
    generated: int
    active: int
    retired: int


@dataclass(frozen=True)
class PipelineState:
    screening: ScreeningState
    watchlist: WatchlistState
    strategy_factory: StrategyFactoryState


@dataclass(frozen=True)
class ExecutionPosition:
    symbol: str
    quantity: float
    exposure: float
    stop_loss: float


@dataclass(frozen=True)
class ExecutionState:
    intents_created: int = 0
    intents_blocked: int = 0
    blocked_reasons: Dict[str, int] = field(default_factory=dict)
    positions: List[ExecutionPosition] = field(default_factory=list)
    fills: int = 0


@dataclass(frozen=True)
class StrategySnapshot:
    strategy_id: str
    age_days: int
    health_score: float
    drawdown: float
    trailing_sl: float
    status: str


@dataclass(frozen=True)
class StrategyState:
    active: List[StrategySnapshot] = field(default_factory=list)
    at_risk: List[StrategySnapshot] = field(default_factory=list)
    retiring: List[StrategySnapshot] = field(default_factory=list)
    retired: List[StrategySnapshot] = field(default_factory=list)


@dataclass(frozen=True)
class RiskState:
    checks_passed: int = 0
    checks_failed: int = 0
    dominant_violation: Optional[str] = None
    freeze_active: bool = False


@dataclass(frozen=True)
class CapitalState:
    total_capital: float = 0.0
    allocated_capital: float = 0.0
    free_capital: float = 0.0
    utilization_ratio: float = 0.0
    throttle_active: bool = False


@dataclass(frozen=True)
class ShadowState:
    enabled: bool = False
    decisions_mirrored: int = 0
    divergences_detected: int = 0
    last_divergence_reason: Optional[str] = None


@dataclass(frozen=True)
class PaperState:
    pnl: float = 0.0
    drawdown: float = 0.0
    active_positions: int = 0


@dataclass(frozen=True)
class IncidentState:
    open_incidents: int = 0
    total_incidents: int = 0
    last_incident_type: Optional[str] = None
    capital_frozen: bool = False


@dataclass(frozen=True)
class ComplianceState:
    audit_packs_ready: bool = False
    last_bundle_hash: Optional[str] = None
    notarized: bool = False
    regulator_ready: bool = False


@dataclass(frozen=True)
class OpsState:
    human_control: bool = False
    takeover_active: bool = False
    succession_mode: str = "UNKNOWN"
    runbook_link: Optional[str] = None

# =====================================================================
# ROOT SNAPSHOT
# =====================================================================

@dataclass(frozen=True)
class SystemSnapshot:
    meta: SnapshotMeta
    system_health: Any
    market_state: Any
    pipeline_state: Any
    strategy_state: Any
    execution_state: Any
    risk_state: Any
    capital_state: Any
    shadow_state: Any
    paper_state: Any
    incidents: Any
    compliance: Any
    ops_state: Any

    @property
    def fingerprint(self) -> str:
        return self.meta.fingerprint

    # -----------------------------------------------------------------
    # FINGERPRINT PAYLOAD
    # -----------------------------------------------------------------

    def _fingerprint_payload(self) -> Dict[str, Any]:
        def norm(v):
            if v == {}:
                return {"__degraded__": True}
            return _safe_asdict(v)

        return {
            "execution_mode": self.meta.execution_mode,
            "market_status": self.meta.market_status,
            "system_version": self.meta.system_version,
            "failure_count": self.meta.failure_count,
            "failures": dict(sorted(self.meta.failures.items())),
            "system_health": norm(self.system_health),
            "market_state": norm(self.market_state),
            "pipeline_state": norm(self.pipeline_state),
            "strategy_state": norm(self.strategy_state),
            "execution_state": norm(self.execution_state),
            "risk_state": norm(self.risk_state),
            "capital_state": norm(self.capital_state),
            "shadow_state": norm(self.shadow_state),
            "paper_state": norm(self.paper_state),
            "incidents": norm(self.incidents),
            "compliance": norm(self.compliance),
            "ops_state": norm(self.ops_state),
        }

    # -----------------------------------------------------------------
    # SERIALIZATION
    # -----------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meta": self.meta.to_dict(),
            "system_health": _safe_asdict(self.system_health),
            "market_state": _safe_asdict(self.market_state),
            "pipeline_state": _safe_asdict(self.pipeline_state),
            "strategy_state": _safe_asdict(self.strategy_state),
            "execution_state": _safe_asdict(self.execution_state),
            "risk_state": _safe_asdict(self.risk_state),
            "capital_state": _safe_asdict(self.capital_state),
            "shadow_state": _safe_asdict(self.shadow_state),
            "paper_state": _safe_asdict(self.paper_state),
            "incidents": _safe_asdict(self.incidents),
            "compliance": _safe_asdict(self.compliance),
            "ops_state": _safe_asdict(self.ops_state),
        }

    # -----------------------------------------------------------------
    # DESERIALIZATION
    # -----------------------------------------------------------------

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SystemSnapshot":
        payload = dict(payload)
        meta_in = SnapshotMeta.from_dict(payload.pop("meta"))

        state = {
            "system_health": _rehydrate(SystemHealth, payload.get("system_health", {}), allow_empty=True),
            "market_state": _rehydrate(MarketState, payload.get("market_state", {}), allow_empty=True),
            "pipeline_state": _rehydrate(PipelineState, payload.get("pipeline_state", {}), allow_empty=True),
            "strategy_state": _rehydrate(StrategyState, payload.get("strategy_state", {}), allow_empty=True),
            "execution_state": _rehydrate(ExecutionState, payload.get("execution_state", {}), allow_empty=True),
            "risk_state": _rehydrate(RiskState, payload.get("risk_state", {}), allow_empty=True),
            "capital_state": _rehydrate(CapitalState, payload.get("capital_state", {}), allow_empty=True),
            "shadow_state": _rehydrate(ShadowState, payload.get("shadow_state", {}), allow_empty=True),
            "paper_state": _rehydrate(PaperState, payload.get("paper_state", {}), allow_empty=True),
            "incidents": _rehydrate(IncidentState, payload.get("incidents", {}), allow_empty=True),
            "compliance": _rehydrate(ComplianceState, payload.get("compliance", {}), allow_empty=True),
            "ops_state": _rehydrate(OpsState, payload.get("ops_state", {}), allow_empty=True),
        }

        temp = cls(meta=meta_in, **state)

        fingerprint = compute_snapshot_fingerprint(temp)
        payload_hash = hashlib.sha256(
            _canonical_json(temp._fingerprint_payload())
        ).hexdigest()

        final_meta = SnapshotMeta(
            snapshot_id=f"SNAPSHOT_{uuid.uuid4().hex}",
            created_at=datetime.utcnow(),
            execution_mode=meta_in.execution_mode,
            market_status=meta_in.market_status,
            system_version=meta_in.system_version,
            failures=meta_in.failures,
            failure_count=meta_in.failure_count,
            is_degraded=meta_in.is_degraded,
            schema_version=meta_in.schema_version,
            fingerprint=fingerprint,
            payload_hash=payload_hash,
        )

        return cls(meta=final_meta, **state)