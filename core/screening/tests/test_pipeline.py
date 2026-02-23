from core.screening.pipeline import run_screening
from core.live_ops.screening import ScreeningResult


def test_pipeline_outputs_contracts():
    results = run_screening()

    assert len(results) > 0

    for r in results:
        assert isinstance(r, ScreeningResult)
        assert isinstance(r.symbol, str)
        assert isinstance(r.reasons, list)
        assert 0.0 <= r.score <= 1.0


def test_pipeline_is_deterministic():
    r1 = run_screening()
    r2 = run_screening()

    assert r1 == r2
