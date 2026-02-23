import pytest

from core.v2.research.experiments.base import (
    ResearchExperiment,
    ExperimentContext,
)
from core.v2.research.evaluators.leakage_guard import LeakageViolation


class CleanExperiment(ResearchExperiment):
    def load(self):
        pass

    def run(self):
        return 1

    def evaluate(self, raw):
        return {"value": raw}


class BadExperiment(ResearchExperiment):
    def load(self):
        import execution  # forbidden
        pass

    def run(self):
        return 1

    def evaluate(self, raw):
        return {"value": raw}


def _ctx():
    return ExperimentContext(
        experiment_id="exp-test",
        dataset_id="ds-test",
        seed=0,
        metadata={},
    )


def test_clean_experiment_passes_leakage_guard():
    exp = CleanExperiment(_ctx())
    exp.execute()  # should not raise


def test_forbidden_import_triggers_violation():
    exp = BadExperiment(_ctx())

    with pytest.raises(LeakageViolation):
        exp.execute()
