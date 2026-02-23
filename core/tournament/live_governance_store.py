import json
from pathlib import Path
from typing import List

from core.tournament.live_governance_contracts import LiveGovernanceDecision


class LiveGovernanceStore:
    """
    Append-only store for LIVE governance decisions.
    """

    def __init__(self, root_dir: str = "tournament/live_governance"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def persist(self, decision: LiveGovernanceDecision) -> None:
        run_dir = self.root / decision.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        path = run_dir / f"{decision.strategy_id}.json"

        # Immutable rule
        if path.exists():
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

        out: List[dict] = []
        for p in sorted(run_dir.glob("*.json")):
            with open(p, "r", encoding="utf-8") as f:
                out.append(json.load(f))
        return out
