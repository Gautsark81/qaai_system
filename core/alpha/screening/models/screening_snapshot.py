from dataclasses import dataclass
from typing import List

from core.alpha.screening.models.screening_verdict import ScreeningVerdict


@dataclass(frozen=True)
class ScreeningSnapshot:
    """
    Immutable snapshot of a screening run.

    Used for:
    - Audit
    - Replay
    - Visual proof
    - Regression validation
    """

    run_id: str
    verdicts: List[ScreeningVerdict]

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "verdicts": [v.to_dict() for v in self.verdicts],
        }
