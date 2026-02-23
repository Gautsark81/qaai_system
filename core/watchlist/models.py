from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass(frozen=True)
class WatchlistEntry:
    symbol: str
    rank: int
    confidence: float
    source: str
    reasons: List[str] = field(default_factory=list)

    # legacy dict-style access
    def __getitem__(self, key):
        return getattr(self, key)


@dataclass(frozen=True)
class WatchlistManifest:
    generated_at: datetime
    entries: List[WatchlistEntry]
    constraints: dict


@dataclass
class WatchlistSnapshot:
    entries: List[WatchlistEntry]
    created_ts: str
    source: str = "screening"
    version: str = "v1"
