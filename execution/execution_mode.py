from enum import Enum


class ExecutionMode(str, Enum):
    DRY_RUN = "dry_run"
    LIVE = "live"
