from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class FingerprintDiff:
    from_version: int
    to_version: int
    breaking_changes: List[str]
    non_breaking_changes: List[str]
    risk_relevant_changes: List[str]
    execution_relevant_changes: List[str]
