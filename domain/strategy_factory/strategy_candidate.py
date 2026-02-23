from dataclasses import dataclass
from typing import Optional
from domain.behavior_fingerprint.fingerprint import StrategyBehaviorFingerprint


@dataclass(frozen=True)
class StrategyCandidate:
    strategy_id: str
    fingerprint: StrategyBehaviorFingerprint
    ssr: Optional[float]
    eligible: bool
    rejection_reason: Optional[str]
