# core/runtime/production_guard.py
from core.runtime.release_lock import ReleaseLock
from core.runtime.system_authorizer import SystemAuthorizer


class ProductionGuard:
    def __init__(
        self,
        *,
        env: str,
        release_lock: ReleaseLock,
        authorizer: SystemAuthorizer,
        execution_guard_armed: bool,
    ):
        self.env = env
        self.release_lock = release_lock
        self.authorizer = authorizer
        self.execution_guard_armed = execution_guard_armed

    def authorize_or_raise(self, lifecycle_state):
        if self.env != "LIVE":
            raise RuntimeError("Not in LIVE environment")

        self.release_lock.verify()

        result = self.authorizer.authorize(
            lifecycle_state=lifecycle_state,
            execution_guard_armed=self.execution_guard_armed,
        )

        if not result.allowed:
            raise RuntimeError(f"Execution blocked: {result.reason}")
