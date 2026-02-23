from __future__ import annotations

from dataclasses import dataclass, field, is_dataclass, asdict
from typing import List, Dict, Any, Union
import hashlib
import json


# ======================================================
# Alpha Genome — Declarative Strategy DNA (V3.2)
# ======================================================

@dataclass(frozen=True)
class AlphaGenome:
    """
    Canonical, declarative representation of a strategy.

    This is NOT execution logic.
    This is NOT signals.
    This is NOT indicators.

    It is a specification that other engines interpret.
    """

    # ---- Context Awareness (NON-BINDING) ----
    allowed_regimes: List[str]

    # ---- Signal Primitive ----
    signal_type: str

    # ---- Filters (All must pass) ----
    filters: List[str] = field(default_factory=list)

    # ---- Risk Control ----
    risk_model: str = "fixed_stop"

    # ---- Exit Logic ----
    exit_model: str = "time_decay"

    # ---- Position Sizing ----
    sizing_model: str = "fixed_fraction"

    # ---- Hyperparameters (Fully declarative) ----
    parameters: Dict[str, Any] = field(default_factory=dict)

    # ---- Versioning ----
    version: str = "v3.2"

    def fingerprint(self) -> str:
        """
        Stable hash for identity, deduplication, and audit.
        """
        return compute_strategy_dna(self)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["fingerprint"] = self.fingerprint()
        return payload


# ======================================================
# Strategy DNA Functional Adapter (CANONICAL)
# ======================================================

def compute_strategy_dna(
    strategy_spec: Any,
) -> str:
    """
    Compute a deterministic DNA hash for a strategy.

    Accepted inputs:
    - AlphaGenome
    - dict
    - dataclass-based specs (e.g. StrategySpec)

    Rules:
    - Pure function
    - Deterministic
    - Order-invariant
    - Identity-only
    """

    payload = _to_payload(strategy_spec)
    normalized = _normalize(payload)

    canonical = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ======================================================
# Internal Helpers
# ======================================================

def _to_payload(obj: Any) -> Dict[str, Any]:
    """
    Convert supported objects into a hashable payload.
    """

    if isinstance(obj, AlphaGenome):
        return _strip_fingerprint(asdict(obj))

    if isinstance(obj, dict):
        return _strip_fingerprint(obj)

    if is_dataclass(obj):
        return _strip_fingerprint(asdict(obj))

    raise TypeError(
        f"compute_strategy_dna does not support type: {type(obj).__name__}"
    )


def _strip_fingerprint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove fingerprint field if present.
    """
    return {k: v for k, v in payload.items() if k != "fingerprint"}


def _normalize(obj: Any) -> Any:
    """
    Recursively normalize payload to ensure order invariance.
    """

    if isinstance(obj, dict):
        return {k: _normalize(obj[k]) for k in sorted(obj)}

    if isinstance(obj, (list, tuple)):
        return [_normalize(x) for x in obj]

    if isinstance(obj, set):
        return sorted(_normalize(x) for x in obj)

    if isinstance(obj, frozenset):
        return sorted((_normalize(k), _normalize(v)) for k, v in obj)

    return obj
