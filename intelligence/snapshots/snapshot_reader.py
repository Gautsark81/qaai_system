from pathlib import Path
from typing import List
from .json_storage import JsonLineStorage
from .snapshot_models import StrategyMetricsSnapshot


class SnapshotReader:
    def __init__(self, root: Path):
        self.storage = JsonLineStorage(root)

    # --------------------------------------------------
    def list_strategies(self) -> List[str]:
        return [p.stem for p in self.storage.root.glob("*.jsonl")]

    # --------------------------------------------------
    def history(self, strategy_id: str) -> List[StrategyMetricsSnapshot]:
        return list(self.storage.read(strategy_id))

    # --------------------------------------------------
    def latest(self, strategy_id: str) -> StrategyMetricsSnapshot | None:
        snaps = self.history(strategy_id)
        return snaps[-1] if snaps else None
