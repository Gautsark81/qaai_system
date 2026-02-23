from __future__ import annotations

from typing import List
from .models import LiveProofArtifact


class LiveProofRegistry:
    """
    Append-only registry of LiveProofArtifact.

    Design Principles:
    - No mutation of stored artifacts
    - No direct access to internal list
    - Defensive copy on read
    - Clear() allowed ONLY for controlled test environments
    """

    def __init__(self):
        self._artifacts: List[LiveProofArtifact] = []

    # ---------------------------------------------------------
    # Write API
    # ---------------------------------------------------------

    def append(self, artifact: LiveProofArtifact) -> None:
        """
        Append artifact to registry.

        No validation here — validation must happen upstream.
        """
        self._artifacts.append(artifact)

    # ---------------------------------------------------------
    # Read API
    # ---------------------------------------------------------

    def list(self) -> List[LiveProofArtifact]:
        """
        Return defensive copy of artifacts.
        """
        return list(self._artifacts)

    def __len__(self) -> int:
        return len(self._artifacts)

    # ---------------------------------------------------------
    # Controlled Reset (Test-Only)
    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Clears registry.

        This exists ONLY to allow deterministic test isolation.
        Must NOT be used in production flows.
        """
        self._artifacts.clear()