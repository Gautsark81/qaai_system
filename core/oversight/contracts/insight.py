from dataclasses import dataclass
from datetime import datetime
from typing import List

from core.oversight.contracts.observation import OversightObservation


@dataclass(frozen=True)
class OversightInsight:
    """
    Aggregated, operator-facing oversight insight.

    Built ONLY from observations.
    """

    insight_id: str
    title: str
    summary: str

    observations: List[OversightObservation]

    severity: str                  # INFO | WARNING | CRITICAL
    generated_at: datetime
