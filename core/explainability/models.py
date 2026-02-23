from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ExplanationArtifact:
    title: str
    body: str
    severity: Optional[str] = None
