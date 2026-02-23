from core.dashboard_read.snapshot import (
    PipelineState,
    ScreeningState,
    WatchlistState,
    StrategyFactoryState,
)
from core.dashboard_read.providers._sources import pipeline as pipeline_source


def build_pipeline_state() -> PipelineState:
    metrics = pipeline_source.read_pipeline_metrics()

    screening = ScreeningState(
        symbols_seen=metrics.screening.symbols_seen,
        passed=metrics.screening.passed,
        rejected_by_reason=metrics.screening.rejected_by_reason,
    )

    watchlist = WatchlistState(
        added=metrics.watchlist.added,
        removed=metrics.watchlist.removed,
        active=metrics.watchlist.active,
    )

    strategy_factory = StrategyFactoryState(
        generated=metrics.strategy_factory.generated,
        active=metrics.strategy_factory.active,
        retired=metrics.strategy_factory.retired,
    )

    return PipelineState(
        screening=screening,
        watchlist=watchlist,
        strategy_factory=strategy_factory,
    )
