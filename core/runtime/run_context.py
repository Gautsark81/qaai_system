from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RunContext:
    run_id: str
    git_commit: str
    phase_version: str
    config_fingerprint: str
    start_time: datetime
