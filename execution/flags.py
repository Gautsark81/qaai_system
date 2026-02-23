from enum import Enum


class ExecutionMode(Enum):
    DRY_RUN = "dry_run"
    LIVE = "live"


class ExecutionFlags:
    def __init__(self):
        self._mode = ExecutionMode.DRY_RUN

    def set_mode(self, mode: ExecutionMode):
        if not isinstance(mode, ExecutionMode):
            raise ValueError("Invalid ExecutionMode")
        self._mode = mode

    def mode(self) -> ExecutionMode:
        return self._mode

    def is_live(self) -> bool:
        return self._mode == ExecutionMode.LIVE

    def is_dry_run(self) -> bool:
        return self._mode == ExecutionMode.DRY_RUN
