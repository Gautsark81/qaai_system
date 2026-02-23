from datetime import datetime, timezone

from core.strategy_factory.health.death_attribution import DeathAttribution
from core.strategy_factory.health.death_reason import DeathReason


def test_death_attribution_fields():
    ts = datetime.now(timezone.utc)

    da = DeathAttribution(
        strategy_id="strat_001",
        reason=DeathReason.MAX_DRAWDOWN,
        timestamp=ts,
        triggered_by="health_engine",
        metrics={
            "drawdown": -0.27,
            "equity_peak": 120000,
            "equity_now": 87600,
        },
    )

    assert da.strategy_id == "strat_001"
    assert da.reason == DeathReason.MAX_DRAWDOWN
    assert da.timestamp == ts
    assert da.triggered_by == "health_engine"
    assert da.metrics["drawdown"] == -0.27


def test_death_attribution_is_immutable():
    da = DeathAttribution(
        strategy_id="s1",
        reason=DeathReason.SSR_FAILURE,
        timestamp=datetime.now(timezone.utc),
        triggered_by="fitness_monitor",
        metrics={"ssr": 0.41},
    )

    try:
        da.reason = DeathReason.OPERATOR_KILL
        assert False, "DeathAttribution should be immutable"
    except AttributeError:
        pass


def test_death_attribution_repr():
    da = DeathAttribution(
        strategy_id="s2",
        reason=DeathReason.OPERATOR_KILL,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        triggered_by="operator",
        metrics={},
    )

    text = repr(da)
    assert "s2" in text
    assert "operator_kill" in text
