# core/runtime/operator_override.py
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class OperatorOverride:
    reason: str
    scope: str
    expires_at: float

    def is_active(self) -> bool:
        return time.time() < self.expires_at


class OperatorOverrideRegistry:
    def __init__(self):
        self._overrides: list[OperatorOverride] = []

    def register(self, override: OperatorOverride):
        if not override.reason or not override.scope:
            raise ValueError("Override must declare reason and scope")
        self._overrides.append(override)

    def active_overrides(self):
        return [o for o in self._overrides if o.is_active()]
