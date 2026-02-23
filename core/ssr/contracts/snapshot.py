from dataclasses import dataclass
from datetime import datetime
from .enums import SSRStatus
from .components import SSRComponentScore
from .flags import SSRFlag


@dataclass(frozen=True)
class SSRSnapshot:
    """
    Immutable, audit-grade SSR snapshot.
    """
    strategy_id: str
    as_of: datetime

    ssr: float
    status: SSRStatus

    components: dict[str, SSRComponentScore]

    trailing_metrics: dict[str, float]
    confidence: float

    flags: list[SSRFlag]
    version: str

    def __post_init__(self):
        if not (0.0 <= self.ssr <= 1.0):
            raise ValueError("SSR must be in [0,1]")

        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be in [0,1]")
