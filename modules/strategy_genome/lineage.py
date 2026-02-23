from dataclasses import dataclass
from typing import Optional


# ==========================================================
# LINEAGE EVENT
# ==========================================================

@dataclass(frozen=True)
class LineageRecord:
    """
    Immutable lineage event.
    """

    strategy_id: str
    parent_id: Optional[str]

    generation: int
    mutation_reason: Optional[str]

    created_by: str            # e.g. "evolution_engine"
