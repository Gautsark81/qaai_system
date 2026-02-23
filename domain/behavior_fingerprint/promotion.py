from dataclasses import dataclass
from .diff import FingerprintDiff
from .governance import GovernanceFingerprint


@dataclass(frozen=True)
class PromotionEligibility:
    from_stage: str
    to_stage: str
    fingerprint_version: int
    diff: FingerprintDiff
    governance: GovernanceFingerprint
    allowed: bool
    reason: str
