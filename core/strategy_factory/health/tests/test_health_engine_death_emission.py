from datetime import datetime, timezone

from core.strategy_factory.health.health_engine import HealthEngine
from core.strategy_factory.health.death_reason import DeathReason
from core.strategy_factory.health.death_attribution import DeathAttribution


class DummyClock:
    def now(self):
        return datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_health_engine_emits_death_attribution_on_kill():
    engine = HealthEngine(clock=DummyClock())

    result = engine.evaluate_and_maybe_kill(
        strategy_id="strat_X",
        equity_curve=[100000, 95000, 87000],
        ssr=0.32,
    )

    assert isinstance(result, DeathAttribution)
    assert result.strategy_id == "strat_X"
    assert result.reason == DeathReason.MAX_DRAWDOWN
    assert result.triggered_by == "health_engine"
    assert result.timestamp.year == 2026
    assert "drawdown" in result.metrics
