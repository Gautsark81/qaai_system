from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .models import (
    PortfolioCapitalPosture,
    CapitalCorrelationConcentrationView,
    PortfolioStressEnvelope,
)


@dataclass(frozen=True)
class CapitalGovernanceSnapshot:
    posture: Optional[PortfolioCapitalPosture]
    correlation_and_concentration: Optional[
        CapitalCorrelationConcentrationView
    ]
    stress_envelope: Optional[PortfolioStressEnvelope]
    generated_at: datetime
    snapshot_version: str
