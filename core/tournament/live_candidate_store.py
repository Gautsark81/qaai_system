import json
from pathlib import Path
from typing import Iterable, List

from core.tournament.live_candidate_artifact import LiveCandidateArtifact


class LiveCandidateStore:
    """
    Append-only store for live candidate artifacts.
    """

    def __init__(self, root_dir: str = "tournament/live_candidates"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def persist(self, artifacts: Iterable[LiveCandidateArtifact]) -> None:
        for a in artifacts:
            self._write(a)

    def _write(self, a: LiveCandidateArtifact) -> None:
        run_dir = self.root / a.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / f"{a.strategy_id}.json"

        if path.exists():
            return  # immutable

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "run_id": a.run_id,
                    "strategy_id": a.strategy_id,
                    "promoted": a.promoted,
                    "reasons": a.reasons,
                    "paper_version": a.paper_version,
                    "live_promotion_version": a.live_promotion_version,
                    "created_at": a.created_at.isoformat(),
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
