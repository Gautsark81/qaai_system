import json
from pathlib import Path
from typing import Iterable
from .snapshot_models import StrategyMetricsSnapshot


class JsonLineStorage:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    def write(self, snapshot: StrategyMetricsSnapshot):
        path = self.root / f"{snapshot.strategy_id}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(snapshot.to_dict()) + "\n")

    # --------------------------------------------------
    def read(self, strategy_id: str) -> Iterable[StrategyMetricsSnapshot]:
        path = self.root / f"{strategy_id}.jsonl"
        if not path.exists():
            return []

        snapshots = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                raw = json.loads(line)
                snapshots.append(StrategyMetricsSnapshot.from_dict(raw))
        return snapshots
