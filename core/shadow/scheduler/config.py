from dataclasses import dataclass


@dataclass(frozen=True)
class ShadowSchedulerConfig:
    """
    Explicit configuration for Shadow Scheduler.

    Default is OFF.
    Shadow must never be implicitly enabled.
    """
    enable_shadow_scheduler: bool = False
