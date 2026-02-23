import pytest
from typing import Any

from core.v2.research.experiments.base import (
    ResearchExperiment,
    ExperimentContext,
    ResearchExperimentError,
)
from core.v2.research.results import ResearchResult


class DummyExperiment(ResearchExperiment):
    def load(self) -> None:
        self.data = [1, 2, 3]

    def run(self) -> Any:
        return sum(self.data)

    def evaluate(self, raw: Any):
        return {"sum": raw}


def test_experiment_executes_successfully():
    ctx = ExperimentContext(
        experiment_id="exp-1",
        dataset_id="ds-1",
        seed=42,
        metadata={"purpose": "unit-test"},
    )

    exp = DummyExperiment(ctx)
    result = exp.execute()

    assert isinstance(result, ResearchResult)
    assert result.experiment_id == "exp-1"
    assert result.dataset_id == "ds-1"
    assert result.metrics["sum"] == 6


def test_missing_experiment_id_fails():
    ctx = ExperimentContext(
        experiment_id="",
        dataset_id="ds-1",
        seed=0,
        metadata={},
    )

    with pytest.raises(ResearchExperimentError):
        DummyExperiment(ctx).execute()


def test_experiment_cannot_be_reused():
    ctx = ExperimentContext(
        experiment_id="exp-reuse",
        dataset_id="ds-1",
        seed=1,
        metadata={},
    )

    exp = DummyExperiment(ctx)
    exp.execute()

    with pytest.raises(RuntimeError):
        exp.execute()
