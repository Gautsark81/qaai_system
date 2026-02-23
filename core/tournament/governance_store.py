# core/tournament/governance_store.py

import json
from pathlib import Path
from typing import List

from core.tournament.governance_contracts import GovernanceDecision


class GovernanceStore:
    """
    Append-only store for governance decisions.
    """

    def __init__(self, root_dir: str = "tournament/governance"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def persist(self, decision: GovernanceDecision) -> None:
        run_dir = self.root / decision.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        path = run_dir / f"{decision.strategy_id}.json"

        if path.exists():
            # Governance decisions are immutable
            return

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "run_id": decision.run_id,
                    "strategy_id": decision.strategy_id,
                    "status": decision.status.value,
                    "reviewer": decision.reviewer,
                    "reasons": decision.reasons,
                    "decided_at": decision.decided_at.isoformat(),
                },
                f,
                indent=2,
            )

    def load_run(self, run_id: str) -> List[dict]:
        run_dir = self.root / run_id
        if not run_dir.exists():
            return []

        results = []
        for path in sorted(run_dir.glob("*.json")):
            with open(path, "r", encoding="utf-8") as f:
                results.append(json.load(f))

        return results
