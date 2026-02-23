from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class TournamentResult:
    tournament_id: UUID
    strategy_id: str
    strategy_version: str

    source_stage: str          # BACKTEST | PAPER
    target_stage: str          # PAPER | LIVE_CANDIDATE

    snapshot_id: UUID
    score: float
    rank: int

    eligible: bool
    elimination_reason: str | None

    created_at: datetime
