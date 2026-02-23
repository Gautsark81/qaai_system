from abc import ABC, abstractmethod
from typing import Iterable

from core.execution.replay.results import ReplayResult
from core.execution.replay.diff_models import ReplayDiffReport


class ReplayStore(ABC):
    """
    Append-only store for replay artifacts.
    """

    @abstractmethod
    def append_result(self, result: ReplayResult) -> None:
        """
        Persist a replay result immutably.
        """
        raise NotImplementedError

    @abstractmethod
    def append_diff(self, diff: ReplayDiffReport) -> None:
        """
        Persist a replay diff report immutably.
        """
        raise NotImplementedError

    @abstractmethod
    def get_results_by_execution_id(
        self, execution_id: str
    ) -> Iterable[ReplayResult]:
        """
        Retrieve all replay results for an execution_id.
        """
        raise NotImplementedError

    @abstractmethod
    def get_diffs_by_execution_id(
        self, execution_id: str
    ) -> Iterable[ReplayDiffReport]:
        """
        Retrieve all replay diffs for an execution_id.
        """
        raise NotImplementedError
