from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from core.v2.research.contracts import ResearchExperimentError
from core.v2.research.manifest import ResearchRunManifest
from core.v2.research.results import ResearchResult


@dataclass(frozen=True)
class AuditEvidenceBundle:
    """
    Immutable bundle of research evidence for audit and review.
    """
    manifests: List[ResearchRunManifest]
    results: List[ResearchResult]

    # Optional evaluator rollups (e.g., SSR, stability summaries)
    evaluator_summaries: Dict[str, Dict] = field(default_factory=dict)

    # Deterministic bundle identity
    bundle_id: str = field(init=False)

    def __post_init__(self) -> None:
        self._validate_consistency()
        object.__setattr__(self, "bundle_id", self._compute_bundle_id())

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_consistency(self) -> None:
        if not self.manifests:
            raise ResearchExperimentError("Bundle must contain at least one manifest")

        manifest_by_result = {m.result_id: m for m in self.manifests}
        result_ids = {r.result_id for r in self.results}

        # Every manifest must have a corresponding result
        for rid in manifest_by_result:
            if rid not in result_ids:
                raise ResearchExperimentError(
                    f"Manifest references missing result_id: {rid}"
                )

    # ------------------------------------------------------------------
    # Deterministic identity
    # ------------------------------------------------------------------

    def _compute_bundle_id(self) -> str:
        h = hashlib.sha256()

        for mid in sorted(m.manifest_id for m in self.manifests):
            h.update(mid.encode())

        for rid in sorted(r.result_id for r in self.results):
            h.update(rid.encode())

        return h.hexdigest()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict:
        """
        JSON-safe representation of the audit bundle.
        """
        return {
            "bundle_id": self.bundle_id,
            "manifests": [m.__dict__ for m in self.manifests],
            "results": [r.__dict__ for r in self.results],
            "evaluator_summaries": self.evaluator_summaries,
        }
