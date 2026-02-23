from .execution_mode import ExecutionMode


class ExecutionFlags:
    """
    Single source of truth for execution mode.
    Default is DRY_RUN.
    """

    def __init__(self):
        self._mode = ExecutionMode.DRY_RUN

    def set_live(self):
        self._mode = ExecutionMode.LIVE

    def set_dry_run(self):
        self._mode = ExecutionMode.DRY_RUN

    def set_mode(self, mode):
        self._mode = mode
        return self

    def mode(self):
        return self._mode

    def is_live(self):
        return self._mode == ExecutionMode.LIVE