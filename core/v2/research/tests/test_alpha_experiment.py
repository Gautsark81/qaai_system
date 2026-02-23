from core.v2.research.experiments.alpha_experiment import AlphaExperiment
from core.v2.research.experiments.base import ExperimentContext
from core.v2.research.contracts import ResearchExperimentError


def _context(returns, regime):
    return ExperimentContext(
        experiment_id="alpha",
        dataset_id="ds",
        seed=0,
        metadata={
            "snapshot_data": {
                "returns": returns,
            },
            "regime": regime,
        },
    )


def test_alpha_experiment_runs():
    returns = [0.01, 0.02, -0.01, 0.03]

    exp = AlphaExperiment(_context(returns, "TRENDING"))
    result = exp.execute()

    assert result.metrics["regime"] == "TRENDING"
    assert result.metrics["outcomes"] == [True, False, True]


def test_alpha_experiment_missing_regime_fails():
    ctx = ExperimentContext(
        experiment_id="alpha",
        dataset_id="ds",
        seed=0,
        metadata={"snapshot_data": {"returns": [0.1, -0.1]}},
    )

    with __import__("pytest").raises(ResearchExperimentError):
        AlphaExperiment(ctx).execute()
