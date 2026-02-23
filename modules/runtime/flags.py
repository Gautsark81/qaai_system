# modules/runtime/flags.py

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeFlags:
    LIVE_TRADING: bool = False
    DRY_RUN: bool = False
    AUDIT_ENABLED: bool = False
    METRICS_ENABLED: bool = False
