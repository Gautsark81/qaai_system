from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, List, Optional
from .fingerprint import StrategyBehaviorFingerprint
from .enums import LifecycleStage


@dataclass(frozen=True)
class FingerprintRecord:
    strategy_id: str
    fingerprint_version: int
    fingerprint: StrategyBehaviorFingerprint
    parent_fingerprint_version: Optional[int]
    lifecycle_stage: LifecycleStage
    created_ts: datetime
    created_by: str


class FingerprintStore(Protocol):

    def save(self, record: FingerprintRecord) -> None: ...

    def load_latest(self, strategy_id: str) -> FingerprintRecord: ...

    def load_version(self, strategy_id: str, version: int) -> FingerprintRecord: ...

    def list_versions(self, strategy_id: str) -> List[int]: ...
