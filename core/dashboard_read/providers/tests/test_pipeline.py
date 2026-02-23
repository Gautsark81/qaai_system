from core.dashboard_read.providers.pipeline import build_pipeline_state
from core.dashboard_read.snapshot import PipelineState


def test_pipeline_state(monkeypatch):
    class DummyScreening:
        symbols_seen = 100
        passed = 40
        rejected_by_reason = {"liquidity": 60}

    class DummyWatchlist:
        added = 5
        removed = 2
        active = 20

    class DummyStrategyFactory:
        generated = 3
        active = 2
        retired = 1

    class DummyPipelineMetrics:
        screening = DummyScreening()
        watchlist = DummyWatchlist()
        strategy_factory = DummyStrategyFactory()

    monkeypatch.setattr(
        "core.dashboard_read.providers._sources.pipeline.read_pipeline_metrics",
        lambda: DummyPipelineMetrics(),
    )

    state = build_pipeline_state()

    assert isinstance(state, PipelineState)
    assert state.watchlist.active == 20
    assert state.strategy_factory.generated == 3
