from __future__ import annotations
from typing import Dict
import uuid


def spawn_lineage(parent_lineage: Dict, mutation_type: str) -> Dict:
    return {
        "strategy_id": f"strat_{uuid.uuid4().hex[:10]}",
        "parent": parent_lineage.get("strategy_id"),
        "mutation": mutation_type,
        "generation": parent_lineage.get("generation", 0) + 1,
    }
