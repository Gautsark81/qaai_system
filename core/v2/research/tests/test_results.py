from datetime import timezone

from core.v2.research.results import ResearchResult


def test_research_result_is_immutable():
    result = ResearchResult(
        experiment_id="exp-1",
        dataset_id="ds-1",
        seed=42,
        metrics={"score": 0.9},
        payload_hash="abc123",
    )

    try:
        result.metrics["score"] = 0.1
        mutated = True
    except Exception:
        mutated = False

    assert mutated is False


def test_result_id_is_deterministic():
    r1 = ResearchResult(
        experiment_id="exp",
        dataset_id="ds",
        seed=1,
        metrics={"a": 1},
        payload_hash="hash",
    )

    r2 = ResearchResult(
        experiment_id="exp",
        dataset_id="ds",
        seed=1,
        metrics={"a": 1},
        payload_hash="hash",
    )

    assert r1.result_id == r2.result_id


def test_created_at_is_utc():
    result = ResearchResult(
        experiment_id="exp",
        dataset_id="ds",
        seed=0,
        metrics={},
        payload_hash="x",
    )

    assert result.created_at.tzinfo == timezone.utc
