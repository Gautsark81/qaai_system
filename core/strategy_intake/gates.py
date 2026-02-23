from typing import Iterable, List
from core.strategy_intake.models import SignalCandidate


def gate_min_confidence(
    candidates: Iterable[SignalCandidate],
    min_confidence: float,
) -> List[SignalCandidate]:
    return [
        c for c in candidates
        if c.confidence >= min_confidence
    ]


def gate_max_symbols(
    candidates: Iterable[SignalCandidate],
    max_symbols: int,
) -> List[SignalCandidate]:
    return list(candidates)[:max_symbols]
