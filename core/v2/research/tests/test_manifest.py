from datetime import datetime, timedelta, timezone

from core.v2.research.manifest import ResearchRunManifest
from core.v2.research.results import ResearchResult


def _result():
    return ResearchResult(
        experiment_id="exp",
        dataset_id="ds",
        seed=1,
        metrics={"x": 1},
        payload_hash="payload",
    )


def test_manifest_is_deterministic():
    r = _result()
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    m1 = ResearchRunManifest.from_result(
        result=r,
        snapshot_hash="snap",
        start=start,
        end=end,
    )

    m2 = ResearchRunManifest.from_result(
        result=r,
        snapshot_hash="snap",
        start=start,
        end=end,
    )

    assert m1.manifest_id == m2.manifest_id


def test_manifest_links_result_correctly():
    r = _result()
    start = datetime.now(tz=timezone.utc)
    end = start + timedelta(hours=1)

    manifest = ResearchRunManifest.from_result(
        result=r,
        snapshot_hash="abc",
        start=start,
        end=end,
        evaluator_metrics={"ssr": 0.8},
        metadata={"operator": "test"},
    )

    assert manifest.experiment_id == r.experiment_id
    assert manifest.result_id == r.result_id
    assert manifest.snapshot_hash == "abc"
    assert manifest.evaluator_metrics["ssr"] == 0.8
    assert manifest.created_at.tzinfo == timezone.utc
