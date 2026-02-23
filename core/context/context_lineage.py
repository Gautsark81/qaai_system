# core/context/context_lineage.py

from dataclasses import dataclass
from typing import List, Dict, Any
import hashlib

from core.context.context_visibility import ReadOnlyDict


@dataclass(frozen=True)
class ContextLineage:
    """
    Immutable, audit-only provenance record for a context snapshot.

    Purpose:
    - Explain *where* context came from
    - NEVER influence execution
    - Deterministic and replay-safe
    """

    symbol: str
    source: str
    detector_ids: List[str]
    regimes: List[Any]
    snapshot_hash: str

    def export(self) -> Dict[str, Any]:
        """
        Export lineage for audit.
        Returned object is dict-like but read-only.
        """
        return ReadOnlyDict({
            "symbol": self.symbol,
            "source": self.source,
            "detector_ids": list(self.detector_ids),
            "regimes": [
                r.value if hasattr(r, "value") else str(r)
                for r in self.regimes
            ],
            "snapshot_hash": self.snapshot_hash,
        })

    @staticmethod
    def compute_hash(
        *,
        symbol: str,
        source: str,
        detector_ids: List[str],
        regimes: List[Any],
    ) -> str:
        """
        Deterministic hash — NO wallclock, NO randomness.
        """
        h = hashlib.sha256()
        h.update(symbol.encode())
        h.update(source.encode())

        for d in detector_ids:
            h.update(d.encode())

        for r in regimes:
            val = r.value if hasattr(r, "value") else str(r)
            h.update(val.encode())

        return h.hexdigest()
