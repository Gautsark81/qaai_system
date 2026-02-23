from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
from types import MappingProxyType


@dataclass(frozen=True)
class ResearchResult:
    """
    Immutable output of a V2.2 research experiment.

    This is the ONLY legal output surface for the Research Track.
    """
    experiment_id: str
    dataset_id: str
    seed: int

    # Evaluator outputs only (deeply immutable)
    metrics: Dict[str, Any]

    # Deterministic integrity hash of experiment payload
    payload_hash: str

    # Optional references to upstream evidence artifacts
    evidence_refs: List[str] = field(default_factory=list)

    # Arbitrary but immutable metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Audit timestamp (UTC)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    # Stable, deterministic identifier
    result_id: str = field(init=False)

    def __post_init__(self) -> None:
        # Deep-freeze containers
        object.__setattr__(self, "metrics", MappingProxyType(dict(self.metrics)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        object.__setattr__(self, "evidence_refs", tuple(self.evidence_refs))

        # Compute deterministic result ID
        object.__setattr__(self, "result_id", self._compute_result_id())

    # ------------------------------------------------------------------
    # Deterministic identity
    # ------------------------------------------------------------------

    def _compute_result_id(self) -> str:
        h = hashlib.sha256()
        h.update(self.experiment_id.encode())
        h.update(self.dataset_id.encode())
        h.update(str(self.seed).encode())
        h.update(self.payload_hash.encode())
        return h.hexdigest()
