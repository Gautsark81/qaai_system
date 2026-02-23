from datetime import datetime, timedelta, timezone

import pytest

from core.v2.research.bundle import AuditEvidenceBundle
from core.v2.research.contracts import ResearchExperimentError
from core.v2.research.manifest import ResearchRunManifest
from core.v2.research.results import ResearchResult


def _result(rid: str):
    return ResearchResult(
        experiment_id="exp",
        dataset_id="ds",
        seed=1,
        metrics={"x": 1},
        payload_hash=rid,
    )


def _manifest(result: ResearchResult):
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    return ResearchRunManifest.from_result(
        result=result,
        snapshot_hash="snap",
        start=start,
        end=end,
    )


def test_bundle_builds_and_is_deterministic():
    r1 = _result("a")
    r2 = _result("b")

    m1 = _manifest(r1)
    m2 = _manifest(r2)

    b1 = AuditEvidenceBundle(
        manifests=[m1, m2],
        results=[r1, r2],
    )

    b2 = AuditEvidenceBundle(
        manifests=[m2, m1],  # reversed order
        results=[r2, r1],
    )

    assert b1.bundle_id == b2.bundle_id
    assert b1.bundle_id is not None


def test_bundle_missing_result_fails():
    r = _result("a")
    m = _manifest(r)

    with pytest.raises(ResearchExperimentError):
        AuditEvidenceBundle(
            manifests=[m],
            results=[],  # missing corresponding result
        )


def test_bundle_serialization():
    r = _result("a")
    m = _manifest(r)

    bundle = AuditEvidenceBundle(
        manifests=[m],
        results=[r],
        evaluator_summaries={"ssr": {"value": 0.9}},
    )

    data = bundle.to_dict()

    assert data["bundle_id"] == bundle.bundle_id
    assert "manifests" in data
    assert "results" in data
