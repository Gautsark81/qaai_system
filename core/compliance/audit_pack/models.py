from dataclasses import dataclass, field
from typing import Any, List
from copy import deepcopy


@dataclass(frozen=True)
class AuditArtifact:
    kind: str
    payload: Any


@dataclass
class AuditManifest:
    version: str
    artifact_kinds: List[str]


@dataclass
class AuditPack:
    manifest: AuditManifest
    artifacts: List[AuditArtifact]
    checksum: str

    def serialize(self) -> bytes:
        from .serializer import serialize_pack
        return serialize_pack(self)

    def compute_checksum(self) -> str:
        from .checksum import compute_checksum
        return compute_checksum(self.serialize())

    def clone(self) -> "AuditPack":
        return deepcopy(self)
