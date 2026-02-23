from dataclasses import dataclass
from typing import List

from .snapshot import EnsembleSnapshot
from .retirement import RetirementResult


@dataclass(frozen=True)
class ReplacementQueueResult:
    replacement_slots: List[str]
    snapshot_hash: str


class ReplacementQueueEngine:

    @staticmethod
    def build(
        snapshot: EnsembleSnapshot,
        retirement: RetirementResult,
    ) -> ReplacementQueueResult:

        if not snapshot.retirement_enabled:
            return ReplacementQueueResult(
                replacement_slots=[],
                snapshot_hash=snapshot.snapshot_hash,
            )

        # Deterministic: 1 slot per retirement candidate
        replacement_slots = sorted(retirement.retirement_candidates)

        return ReplacementQueueResult(
            replacement_slots=replacement_slots,
            snapshot_hash=snapshot.snapshot_hash,
        )