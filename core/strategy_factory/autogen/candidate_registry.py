# core/strategy_factory/autogen/candidate_registry.py

from typing import Dict, List
from .candidate_models import (
    StrategyCandidate,
    CandidateStage,
)


class CandidateRegistry:

    def __init__(self):
        self._history: List[StrategyCandidate] = []

    def register_lab_candidate(self, hypothesis_id: str, hypothesis_hash: str):
        candidate = StrategyCandidate(
            hypothesis_id=hypothesis_id,
            hypothesis_hash=hypothesis_hash,
            stage=CandidateStage.LAB,
        )
        self._history.append(candidate)
        return candidate

    def update_stage(
        self,
        hypothesis_id: str,
        new_stage: CandidateStage,
        ssr: float | None = None,
        max_drawdown: float | None = None,
        shadow_cycles: int | None = None,
    ):
        last = self.get_latest(hypothesis_id)

        if last is None:
            raise ValueError("Candidate not found")

        updated = StrategyCandidate(
            hypothesis_id=hypothesis_id,
            hypothesis_hash=last.hypothesis_hash,
            stage=new_stage,
            ssr=ssr if ssr is not None else last.ssr,
            max_drawdown=max_drawdown if max_drawdown is not None else last.max_drawdown,
            shadow_cycles=shadow_cycles if shadow_cycles is not None else last.shadow_cycles,
        )

        self._history.append(updated)
        return updated

    def get_latest(self, hypothesis_id: str) -> StrategyCandidate | None:
        for candidate in reversed(self._history):
            if candidate.hypothesis_id == hypothesis_id:
                return candidate
        return None

    def history(self) -> List[StrategyCandidate]:
        return list(self._history)