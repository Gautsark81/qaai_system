from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

from core.v2.research.results import ResearchResult


@dataclass(frozen=True)
class ResearchRunManifest:
    """
    Immutable audit manifest for a single research run.

    This is the legal record of what ran, on what data, and what came out.
    """
    experiment_id: str
    dataset_id: str
    seed: int

    # Snapshot provenance
    snapshot_hash: str
    start: str
    end: str

    # Result linkage
    result_id: str
    payload_hash: str

    # Optional evaluator summaries
    evaluator_metrics: Dict[str, Any] = field(default_factory=dict)

    # Free-form but immutable metadata (operator, notes, tags)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Audit timestamp
    created_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    # Stable manifest identifier
    manifest_id: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "manifest_id", self._compute_manifest_id())

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_result(
        cls,
        *,
        result: ResearchResult,
        snapshot_hash: str,
        start,
        end,
        evaluator_metrics: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> "ResearchRunManifest":
        """
        Create a manifest directly from a ResearchResult.
        """
        return cls(
            experiment_id=result.experiment_id,
            dataset_id=result.dataset_id,
            seed=result.seed,
            snapshot_hash=snapshot_hash,
            start=start.isoformat(),
            end=end.isoformat(),
            result_id=result.result_id,
            payload_hash=result.payload_hash,
            evaluator_metrics=evaluator_metrics or {},
            metadata=metadata or {},
        )

    # ------------------------------------------------------------------
    # Deterministic identity
    # ------------------------------------------------------------------

    def _compute_manifest_id(self) -> str:
        h = hashlib.sha256()
        h.update(self.experiment_id.encode())
        h.update(self.dataset_id.encode())
        h.update(str(self.seed).encode())
        h.update(self.snapshot_hash.encode())
        h.update(self.result_id.encode())
        return h.hexdigest()
