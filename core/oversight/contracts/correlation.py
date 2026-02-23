from dataclasses import dataclass
from typing import FrozenSet, List, Optional

from core.oversight.contracts.severity import SeverityLevel


@dataclass(frozen=True)
class CorrelatedOversightFinding:
    """
    Result of correlating multiple oversight findings
    across domains.

    Read-only, auditor-safe.
    """

    domains: FrozenSet[str]
    severity: SeverityLevel

    summaries: List[str]
    detectors: FrozenSet[str]

    evidence_ids: FrozenSet[str]
