from typing import List
from core.live_ops.screening import ScreeningResult


def rank_by_score(results: List[ScreeningResult]) -> List[ScreeningResult]:
    """
    Deterministic ranking: highest score first.
    Stable sort for replay safety.
    """
    return sorted(
        results,
        key=lambda r: (-r.score, r.symbol),
    )
