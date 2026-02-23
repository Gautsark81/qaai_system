from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class LeaderboardEntry:
    strategy_id: str
    ssr: float
    net_pnl: float


class Leaderboard:
    def rank(self, entries: List[LeaderboardEntry]) -> List[LeaderboardEntry]:
        return sorted(
            entries,
            key=lambda e: (e.ssr, e.net_pnl),
            reverse=True,
        )
