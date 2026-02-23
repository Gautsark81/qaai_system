from dataclasses import dataclass
from datetime import datetime
from .identity import IdentityFingerprint
from .market_behavior import MarketInteractionFingerprint
from .risk_behavior import RiskExposureFingerprint
from .execution_behavior import ExecutionStyleFingerprint
from .performance_shape import PerformanceShapeFingerprint
from .stability import StabilityFingerprint
from .governance import GovernanceFingerprint


@dataclass(frozen=True)
class FingerprintMeta:
    schema_version: str
    generated_by: str
    generated_ts: datetime
    validation_status: str


@dataclass(frozen=True)
class StrategyBehaviorFingerprint:
    identity: IdentityFingerprint
    market_behavior: MarketInteractionFingerprint
    risk_behavior: RiskExposureFingerprint
    execution_behavior: ExecutionStyleFingerprint
    performance_shape: PerformanceShapeFingerprint
    stability_profile: StabilityFingerprint
    governance_flags: GovernanceFingerprint
    meta: FingerprintMeta
