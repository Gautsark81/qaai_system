from datetime import datetime, timedelta

import pytest

from core.v2.research.datasets.snapshot_loader import (
    SnapshotLoader,
    SnapshotLoaderError,
)


def _provider(start, end):
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "value": 42,
    }


def test_snapshot_loader_returns_immutable_slice():
    loader = SnapshotLoader(dataset_id="ds-1", provider=_provider)

    start = datetime(2020, 1, 1)
    end = start + timedelta(days=1)

    snap = loader.load(start, end)

    assert snap.dataset_id == "ds-1"
    assert snap.data["value"] == 42

    with pytest.raises(TypeError):
        snap.data["value"] = 0


def test_snapshot_loader_hash_is_deterministic():
    loader = SnapshotLoader(dataset_id="ds", provider=_provider)

    start = datetime(2021, 1, 1)
    end = start + timedelta(days=1)

    s1 = loader.load(start, end)
    s2 = loader.load(start, end)

    assert s1.content_hash == s2.content_hash


def test_invalid_time_window_fails():
    loader = SnapshotLoader(dataset_id="ds", provider=_provider)

    t = datetime.utcnow()

    with pytest.raises(SnapshotLoaderError):
        loader.load(t, t)
