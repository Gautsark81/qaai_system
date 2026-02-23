from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, Mapping
from types import MappingProxyType


class SnapshotLoaderError(RuntimeError):
    """Raised when snapshot loading or validation fails."""


@dataclass(frozen=True)
class SnapshotSlice:
    """
    Immutable view of a dataset snapshot slice.
    """
    dataset_id: str
    start: datetime
    end: datetime
    data: Mapping[str, Any]
    content_hash: str


class SnapshotLoader:
    """
    Read-only loader for historical dataset snapshots.

    This is the ONLY legal data ingress for V2.2 research.
    """

    def __init__(
        self,
        dataset_id: str,
        provider: Callable[[datetime, datetime], Dict[str, Any]],
    ):
        """
        Parameters
        ----------
        dataset_id:
            Stable identifier of the dataset.
        provider:
            Callable that returns raw snapshot data for [start, end].
            Must be deterministic and side-effect free.
        """
        self._dataset_id = dataset_id
        self._provider = provider

    def load(self, start: datetime, end: datetime) -> SnapshotSlice:
        """
        Load an immutable snapshot slice for the given time window.
        """
        self._validate_window(start, end)

        raw = self._provider(start, end)
        if not isinstance(raw, dict):
            raise SnapshotLoaderError("Provider must return a dict")

        frozen = MappingProxyType(dict(raw))
        content_hash = self._hash_content(frozen)

        return SnapshotSlice(
            dataset_id=self._dataset_id,
            start=start,
            end=end,
            data=frozen,
            content_hash=content_hash,
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_window(start: datetime, end: datetime) -> None:
        if start >= end:
            raise SnapshotLoaderError("start must be before end")

    @staticmethod
    def _hash_content(data: Mapping[str, Any]) -> str:
        h = hashlib.sha256()
        for key in sorted(data.keys()):
            h.update(str(key).encode())
            h.update(repr(data[key]).encode())
        return h.hexdigest()
