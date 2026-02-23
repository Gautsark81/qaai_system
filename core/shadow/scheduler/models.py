from dataclasses import dataclass


@dataclass(frozen=True)
class ShadowSchedulerEvent:
    """
    Observational-only audit event emitted by Shadow Scheduler.
    """
    kind: str
    is_observational: bool
    has_execution_authority: bool
    has_capital_authority: bool
