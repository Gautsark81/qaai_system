# core/runtime/execution_lock.py
from dataclasses import dataclass
from core.runtime.environment import RuntimeEnvironment

@dataclass(frozen=True)
class ExecutionLock:
    environment: RuntimeEnvironment
    armed: bool

    def can_execute_live(self) -> bool:
        return self.environment.allow_live_execution and self.armed

    def assert_live_allowed(self):
        if not self.can_execute_live():
            raise RuntimeError(
                "Live execution blocked "
                f"(env={self.environment.name}, armed={self.armed})"
            )
