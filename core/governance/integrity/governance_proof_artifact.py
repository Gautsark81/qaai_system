# core/governance/integrity/governance_proof_artifact.py

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from core.governance.integrity.governance_snapshot_hash_engine import (
    GovernanceSnapshotHashEngine,
)
from core.governance.integrity.governance_ledger_fingerprint_engine import (
    GovernanceLedgerFingerprintEngine,
)
from core.governance.reconstruction import GovernanceState


@dataclass(frozen=True)
class GovernanceProofArtifact:
    governance_id: str
    snapshot_hash: str
    ledger_hash: str
    combined_hash: str
    generated_at: datetime


class GovernanceProofEngine:
    """
    Phase C6.4

    Combines snapshot + ledger fingerprint into single immutable proof.
    """

    @staticmethod
    def generate_proof(
        *,
        state: GovernanceState,
        ledgers,
    ) -> GovernanceProofArtifact:

        snapshot_hash = GovernanceSnapshotHashEngine.compute_hash(state)
        ledger_hash = GovernanceLedgerFingerprintEngine.compute_fingerprint(
            ledgers=ledgers
        )

        combined_input = f"{snapshot_hash}|{ledger_hash}"
        combined_hash = hashlib.sha256(combined_input.encode("utf-8")).hexdigest()

        return GovernanceProofArtifact(
            governance_id=state.governance_id,
            snapshot_hash=snapshot_hash,
            ledger_hash=ledger_hash,
            combined_hash=combined_hash,
            generated_at=datetime.now(timezone.utc),
        )