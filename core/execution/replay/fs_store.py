from pathlib import Path
from typing import Iterable

from core.execution.replay.store import ReplayStore
from core.execution.replay.results import ReplayResult
from core.execution.replay.diff_models import ReplayDiffReport
from core.execution.replay.serializer import serialize, deserialize


class FileSystemReplayStore(ReplayStore):
    """
    Append-only filesystem-backed store for replay artifacts.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.results_dir = base_dir / "results"
        self.diffs_dir = base_dir / "diffs"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.diffs_dir.mkdir(parents=True, exist_ok=True)

    def _results_file(self, execution_id: str) -> Path:
        return self.results_dir / f"{execution_id}.jsonl"

    def _diffs_file(self, execution_id: str) -> Path:
        return self.diffs_dir / f"{execution_id}.jsonl"

    def append_result(self, result: ReplayResult) -> None:
        path = self._results_file(result.execution_id)
        with path.open("a", encoding="utf-8") as f:
            f.write(serialize(result) + "\n")

    def append_diff(self, diff: ReplayDiffReport) -> None:
        path = self._diffs_file(diff.execution_id)
        with path.open("a", encoding="utf-8") as f:
            f.write(serialize(diff) + "\n")

    def get_results_by_execution_id(
        self, execution_id: str
    ) -> Iterable[dict]:
        path = self._results_file(execution_id)
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                yield deserialize(line)

    def get_diffs_by_execution_id(
        self, execution_id: str
    ) -> Iterable[dict]:
        path = self._diffs_file(execution_id)
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                yield deserialize(line)
