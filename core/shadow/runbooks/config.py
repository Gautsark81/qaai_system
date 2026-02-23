from dataclasses import dataclass


@dataclass(frozen=True)
class ShadowRunbookConfig:
    """
    Explicit enablement for Shadow Runbooks.
    """
    enable_shadow_runbooks: bool = False
