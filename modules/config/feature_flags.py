from dataclasses import dataclass
from modules.config.runtime_mode import RuntimeMode


@dataclass(frozen=True)
class FeatureFlags:
    ENABLE_PHASE_13: bool = False
    RUNTIME_MODE: RuntimeMode = RuntimeMode.LIVE


def phase13_enabled(flags: FeatureFlags) -> bool:
    return (
        flags.ENABLE_PHASE_13
        and flags.RUNTIME_MODE in {RuntimeMode.SIM, RuntimeMode.BACKTEST}
    )


FEATURE_FLAGS = FeatureFlags()
