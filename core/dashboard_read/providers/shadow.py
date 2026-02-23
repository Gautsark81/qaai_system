from core.dashboard_read.snapshot import ShadowState
from core.dashboard_read.providers._sources import shadow as shadow_source


def build_shadow_state() -> ShadowState:
    """
    Shadow trading state provider.

    Copy-only.
    No logic.
    Schema-accurate.
    """

    metrics = shadow_source.read_shadow_metrics()

    return ShadowState(
        enabled=metrics.enabled,
        decisions_mirrored=metrics.decisions_mirrored,
        divergences_detected=metrics.divergences_detected,
        last_divergence_reason=metrics.last_divergence_reason,
    )
