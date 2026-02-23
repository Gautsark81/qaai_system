from core.dashboard_read.providers.shadow import build_shadow_state
from core.dashboard_read.snapshot import ShadowState


def test_shadow_state(monkeypatch):
    class DummyShadowMetrics:
        enabled = True
        decisions_mirrored = 120
        divergences_detected = 3
        last_divergence_reason = "SLIPPAGE"

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.shadow.read_shadow_metrics",
        lambda: DummyShadowMetrics(),
    )

    state = build_shadow_state()

    assert isinstance(state, ShadowState)
    assert state.enabled is True
    assert state.divergences_detected == 3
