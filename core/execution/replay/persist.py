from core.execution.replay.store import ReplayStore
from core.execution.replay.results import ReplayResult
from core.execution.replay.diff_models import ReplayDiffReport


def persist_replay_result(
    store: ReplayStore,
    result: ReplayResult,
) -> None:
    """
    Persist replay result safely.
    """
    try:
        store.append_result(result)
    except Exception:
        pass


def persist_replay_diff(
    store: ReplayStore,
    diff: ReplayDiffReport,
) -> None:
    """
    Persist replay diff safely.
    """
    try:
        store.append_diff(diff)
    except Exception:
        pass
