from typing import List
from .models import AuditManifest, AuditArtifact


def build_manifest(artifacts: List[AuditArtifact]) -> AuditManifest:
    """
    Deterministic manifest describing audit pack contents.
    """
    kinds = sorted(a.kind for a in artifacts)
    return AuditManifest(
        version="28.2",
        artifact_kinds=kinds,
    )
