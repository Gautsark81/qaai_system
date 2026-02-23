from core.v2.research.experiments.regime_experiment import RegimeExperiment
from core.v2.research.experiments.base import ExperimentContext
from core.v2.research.contracts import ResearchExperimentError


def _context(prices, returns):
    return ExperimentContext(
        experiment_id="regime",
        dataset_id="ds",
        seed=0,
        metadata={
            "snapshot_data": {
                "prices": prices,
                "returns": returns,
            }
        },
    )


def test_regime_experiment_runs():
    prices = [100, 101, 102, 103, 104, 105]
    returns = [0.01, 0.01, 0.01, 0.01, 0.01]

    exp = RegimeExperiment(_context(prices, returns))
    result = exp.execute()

    assert result.metrics["regime"] in {
        "TRENDING",
        "RANGING",
        "CALM",
        "VOLATILE",
    }


def test_regime_experiment_invalid_input_fails():
    ctx = ExperimentContext(
        experiment_id="regime",
        dataset_id="ds",
        seed=0,
        metadata={"snapshot_data": {"prices": [1, 2, 3]}},
    )

    with __import__("pytest").raises(ResearchExperimentError):
        RegimeExperiment(ctx).execute()
