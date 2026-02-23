from dataclasses import dataclass
from typing import Tuple, Any


@dataclass(frozen=True)
class ReplayInputs:
    """
    Deterministic inputs required for replay.
    """
    telemetry_records: Tuple[dict, ...]
    config_snapshot: dict
    environment: dict
