from modules.config.feature_flags import FeatureFlags, phase13_enabled


def assert_phase13_enabled(flags: FeatureFlags) -> None:
    """
    Explicit runtime guard for Phase-13 execution paths.

    Must be called by:
    - SIM orchestrators
    - Backtest runners
    - Capital allocators
    """
    if not phase13_enabled(flags):
        raise RuntimeError(
            "Phase 13 execution attempted while disabled or in LIVE mode."
        )
