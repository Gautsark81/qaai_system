from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass(frozen=True)
class WatchlistEntry:
    symbol: str
    rank: int
    confidence: float
    source: str
    reasons: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class WatchlistManifest:
    generated_at: datetime
    entries: List[WatchlistEntry]
    constraints: Dict[str, float | int]

    @property
    def total(self) -> int:
        return len(self.entries)

    def symbols(self) -> List[str]:
        return [e.symbol for e in self.entries]

    def top(self, n: int) -> List[WatchlistEntry]:
        return self.entries[:n]
