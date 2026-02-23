from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


@dataclass(frozen=True)
class GovernanceChain:
    governance_chain_id: str
    throttle_events: Tuple
    scaling_events: Tuple
    promotion_events: Tuple


@dataclass(frozen=True)
class GovernanceReconstructionResult:
    chains: Tuple[GovernanceChain, ...]
    orphan_events: Tuple
    valid: bool
    errors: Tuple[str, ...]


class GovernanceChainReconstructor:
    """
    Phase C4.6 — Cross-Ledger Governance Reconstruction

    Pure, deterministic, read-only reconstruction engine.
    """

    def reconstruct(
        self,
        *,
        throttle_events: List,
        scaling_events: List,
        promotion_events: List,
    ) -> GovernanceReconstructionResult:

        chains: Dict[str, Dict[str, list]] = {}
        orphan_events = []
        errors = []

        # --------------------------------------------------
        # Collect events by governance_chain_id
        # --------------------------------------------------

        def collect(event, bucket_name: str):
            chain_id = getattr(event, "governance_chain_id", None)

            if not chain_id:
                orphan_events.append(event)
                return

            chains.setdefault(
                chain_id,
                {"throttle": [], "scaling": [], "promotion": []},
            )[bucket_name].append(event)

        for e in throttle_events:
            collect(e, "throttle")

        for e in scaling_events:
            collect(e, "scaling")

        for e in promotion_events:
            collect(e, "promotion")

        reconstructed = []

        # --------------------------------------------------
        # Structural integrity validation
        # --------------------------------------------------

        for chain_id, grouped in chains.items():

            if not grouped["throttle"]:
                errors.append(f"Chain {chain_id} missing throttle event")

            if not grouped["scaling"] and not grouped["promotion"]:
                errors.append(
                    f"Chain {chain_id} has no scaling or promotion event"
                )

            reconstructed.append(
                GovernanceChain(
                    governance_chain_id=chain_id,
                    throttle_events=tuple(grouped["throttle"]),
                    scaling_events=tuple(grouped["scaling"]),
                    promotion_events=tuple(grouped["promotion"]),
                )
            )

        # --------------------------------------------------
        # Orphans invalidate reconstruction
        # --------------------------------------------------

        if orphan_events:
            errors.append("Orphan events detected")

        valid = len(errors) == 0

        return GovernanceReconstructionResult(
            chains=tuple(reconstructed),
            orphan_events=tuple(orphan_events),
            valid=valid,
            errors=tuple(errors),
        )