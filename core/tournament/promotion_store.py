# core/tournament/promotion_store.py

import json
from pathlib import Path
from typing import Iterable, List

from core.tournament.promotion_artifact import PromotionArtifact


class PromotionStore:
    """
    Persists promotion artifacts in an immutable, append-only manner.
    """

    def __init__(self, root_dir: str = "tournament/promotions"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def persist(self, artifacts: Iterable[PromotionArtifact]) -> None:
        for artifact in artifacts:
            self._write_artifact(artifact)

    def _write_artifact(self, artifact: PromotionArtifact) -> None:
        run_dir = self.root / artifact.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        path = run_dir / f"{artifact.strategy_id}.json"

        if path.exists():
            # Immutable rule: never overwrite
            return

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "run_id": artifact.run_id,
                    "strategy_id": artifact.strategy_id,
                    "promoted": artifact.promoted,
                    "reasons": artifact.reasons,
                    "metrics_version": artifact.metrics_version,
                    "promotion_version": artifact.promotion_version,
                    "created_at": artifact.created_at.isoformat(),
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
