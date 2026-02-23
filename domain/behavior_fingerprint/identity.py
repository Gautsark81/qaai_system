from dataclasses import dataclass
from datetime import datetime
from .enums import StrategyFamily, GenerationSource


@dataclass(frozen=True)
class IdentityFingerprint:
    strategy_id: str
    strategy_family: StrategyFamily
    generation_source: GenerationSource
    code_hash: str
    parameter_hash: str
    creation_ts: datetime
