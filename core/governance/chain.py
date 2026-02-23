# core/governance/chain.py

from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class GovernanceChain:
    governance_chain_id: str
    created_at: datetime
    source: str  # screening | scaling | promotion | manual


def generate_governance_chain(source: str) -> GovernanceChain:
    """
    Creates a new immutable governance chain.
    """
    return GovernanceChain(
        governance_chain_id=f"GOV-{uuid.uuid4().hex[:16].upper()}",
        created_at=datetime.utcnow(),
        source=source,
    )