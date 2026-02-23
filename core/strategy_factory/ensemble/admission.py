from dataclasses import dataclass
from typing import Dict, List

from .snapshot import EnsembleSnapshot


@dataclass(frozen=True)
class AdmissionResult:
    approved: List[str]
    rejected: Dict[str, str]
    snapshot_hash: str


class StrategyAdmissionGate:

    @staticmethod
    def evaluate(
        snapshot: EnsembleSnapshot,
        candidates: Dict[str, float],  # strategy_id -> SSR
    ) -> AdmissionResult:

        approved: List[str] = []
        rejected: Dict[str, str] = {}

        for sid, ssr in candidates.items():

            if ssr < snapshot.suspension_min_ssr:
                rejected[sid] = "SSR_BELOW_MINIMUM"
                continue

            # Placeholder diversity rule (deterministic)
            if snapshot.diversity_penalty_strength > 0.9:
                rejected[sid] = "DIVERSITY_BLOCK"
                continue

            approved.append(sid)

        return AdmissionResult(
            approved=sorted(approved),
            rejected=rejected,
            snapshot_hash=snapshot.snapshot_hash,
        )