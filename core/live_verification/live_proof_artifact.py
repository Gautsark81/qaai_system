from __future__ import annotations

from .models import LiveProofArtifact, ExecutionTraceEvidence
from .authority_chain_verifier import AuthorityChainVerifier


class LiveProofBuilder:
    """
    Builds immutable live proof artifact.
    """

    def __init__(self):
        self._verifier = AuthorityChainVerifier()

    def build(self, trace: ExecutionTraceEvidence) -> LiveProofArtifact:
        validated = self._verifier.validate(trace)
        chain_hash = trace.compute_chain_hash()

        return LiveProofArtifact(
            trace=trace,
            chain_hash=chain_hash,
            authority_validated=validated,
        )