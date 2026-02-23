from dataclasses import dataclass
from typing import List

from .snapshot import EnsembleSnapshot
from .replacement import ReplacementQueueResult
from .admission import AdmissionResult


@dataclass(frozen=True)
class ActivationResult:
    activated: List[str]
    skipped: List[str]
    snapshot_hash: str


class StrategyActivationEngine:

    @staticmethod
    def activate(
        snapshot: EnsembleSnapshot,
        replacement: ReplacementQueueResult,
        admission: AdmissionResult,
    ) -> ActivationResult:

        activated: List[str] = []
        skipped: List[str] = []

        available_slots = len(replacement.replacement_slots)

        for sid in admission.approved:

            if available_slots <= 0:
                skipped.append(sid)
                continue

            activated.append(sid)
            available_slots -= 1

        return ActivationResult(
            activated=sorted(activated),
            skipped=sorted(skipped),
            snapshot_hash=snapshot.snapshot_hash,
        )