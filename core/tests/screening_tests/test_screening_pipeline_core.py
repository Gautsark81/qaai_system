from core.screening.pipeline import ScreeningPipeline
from core.screening.engine import ScreeningEngine
from core.screening.rules import LiquidityRule
from core.screening.models import MarketSnapshot


def test_pipeline_batch():
    engine = ScreeningEngine([LiquidityRule(1_000_000)])
    pipeline = ScreeningPipeline(engine)

    snaps = [
        MarketSnapshot("A", 100, 2e6, 2, 0.2, 0.7),
        MarketSnapshot("B", 200, 5e5, 2, 0.2, 0.7),
    ]

    results = pipeline.run(snaps)

    assert results[0].passed is True
    assert results[1].passed is False
