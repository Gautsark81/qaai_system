import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from core.v2.research.cli import replay_from_manifest, ReplayMismatchError
from core.v2.research.registry import ExperimentRegistry, ExperimentSpec
from core.v2.research.experiments.base import ResearchExperiment
from core.v2.research.datasets.snapshot_loader import SnapshotLoader
from core.v2.research.manifest import ResearchRunManifest


class DummyExperiment(ResearchExperiment):
    def load(self):
        pass

    def run(self):
        return 1

    def evaluate(self, raw):
        return {"value": raw}


def _provider(start, end):
    return {"x": 1}


def test_replay_from_manifest_success(tmp_path: Path):
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

    # Run once to get a result
    start = datetime(2020, 1, 1)
    end = start + timedelta(days=1)

    result = registry.run(
        "exp",
        start=start,
        end=end,
        seed=1,
        metadata={},
    )

    manifest = ResearchRunManifest.from_result(
        result=result,
        snapshot_hash="dummy",
        start=start,
        end=end,
    )

    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest.__dict__, default=str))

    replayed = replay_from_manifest(
        manifest_path=path,
        registry=registry,
    )

    assert replayed.manifest_id == manifest.manifest_id


def test_replay_detects_mismatch(tmp_path: Path):
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

    start = datetime(2020, 1, 1)
    end = start + timedelta(days=1)

    bad_manifest = {
        "experiment_id": "exp",
        "dataset_id": "ds",
        "seed": 1,
        "snapshot_hash": "bad",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "result_id": "wrong",
        "payload_hash": "wrong",
        "evaluator_metrics": {},
        "metadata": {},
        "created_at": start.isoformat(),
        "manifest_id": "wrong",
    }

    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(bad_manifest))

    with pytest.raises(ReplayMismatchError):
        replay_from_manifest(
            manifest_path=path,
            registry=registry,
        )
