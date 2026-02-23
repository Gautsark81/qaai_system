from uuid import uuid4
from datetime import datetime

from qaai_system.tournament.filters import apply_hard_filters
from qaai_system.tournament.scoring import score_strategy
from qaai_system.tournament.ranking import rank_strategies
from qaai_system.tournament.models import TournamentResult


class StrategyTournamentEngine:
    """
    Offline tournament engine.
    Produces ranked promotion candidates.
    """

    def run(self, snapshots, *, source_stage: str, target_stage: str):
        tournament_id = uuid4()

        survivors, eliminated = apply_hard_filters(snapshots)

        results = []

        for snap, reason in eliminated:
            results.append(
                TournamentResult(
                    tournament_id=tournament_id,
                    strategy_id=snap.strategy_id,
                    strategy_version=snap.strategy_version,
                    source_stage=source_stage,
                    target_stage=target_stage,
                    snapshot_id=snap.snapshot_id,
                    score=0.0,
                    rank=-1,
                    eligible=False,
                    elimination_reason=reason,
                    created_at=datetime.utcnow(),
                )
            )

        scored = [(snap, score_strategy(snap)) for snap in survivors]
        ranked = rank_strategies(scored)

        for rank, (snap, score) in enumerate(ranked, start=1):
            results.append(
                TournamentResult(
                    tournament_id=tournament_id,
                    strategy_id=snap.strategy_id,
                    strategy_version=snap.strategy_version,
                    source_stage=source_stage,
                    target_stage=target_stage,
                    snapshot_id=snap.snapshot_id,
                    score=score,
                    rank=rank,
                    eligible=True,
                    elimination_reason=None,
                    created_at=datetime.utcnow(),
                )
            )

        return results
