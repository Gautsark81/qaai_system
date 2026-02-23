from datetime import datetime, timedelta

import pytest

from core.v2.research.registry import (
    ExperimentRegistry,
    ExperimentSpec,
)
from core.v2.research.experiments.base import ResearchExperiment
from core.v2.research.datasets.snapshot_loader import SnapshotLoader
from core.v2.research.contracts import ResearchExperimentError


class DummyExperiment(ResearchExperiment):
    def load(self):
        pass

    def run(self):
        return 1

    def evaluate(self, raw):
        return {"value": raw}


def _provider(start, end):
    return {"x": 1}


def test_register_and_list_experiment():
    registry = ExperimentRegistry()
    loader = SnapshotLoader("ds", _provider)

    spec = ExperimentSpec(
        experiment_id="exp-1",
        experiment_cls=DummyExperiment,
        dataset_loader=loader,
        evaluators=[],
    )

    registry.register(spec)

    assert registry.list_experiments() == ["exp-1"]


def test_duplicate_registration_fails():
    registry = ExperimentRegistry()
    loader = SnapshotLoader("ds", _provider)

    spec = ExperimentSpec(
        experiment_id="exp",
        experiment_cls=DummyExperiment,
        dataset_loader=loader,
        evaluators=[],
    )

    registry.register(spec)

    with pytest.raises(ResearchExperimentError):
        registry.register(spec)


def test_unregistered_experiment_fails():
    registry = ExperimentRegistry()

    with pytest.raises(ResearchExperimentError):
        registry.run(
            "missing",
            start=datetime.utcnow(),
            end=datetime.utcnow() + timedelta(days=1),
            seed=0,
            metadata={},
        )


def test_registered_experiment_executes():
    registry = ExperimentRegistry()
    loader = SnapshotLoader("ds", _provider)

    registry.register(
        ExperimentSpec(
            experiment_id="exp",
            experiment_cls=DummyExperiment,
            dataset_loader=loader,
            evaluators=[],
        )
    )

    result = registry.run(
        "exp",
        start=datetime(2020, 1, 1),
        end=datetime(2020, 1, 2),
        seed=1,
        metadata={"purpose": "test"},
    )

    assert result.experiment_id == "exp"
    assert result.metrics["value"] == 1
