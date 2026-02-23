from core.dashboard_read.replay.failures import (
    ReplayFailure,
    IntegrityFailure,
    SchemaMismatch,
    MissingEvidence,
    ReplayInvariantViolation,
    UnsupportedReplay,
)


def test_failure_types_are_data_objects():
    failure = IntegrityFailure(reason="hash mismatch")

    assert isinstance(failure, ReplayFailure)
    assert failure.reason == "hash mismatch"


def test_all_failure_types_instantiable():
    failures = [
        IntegrityFailure("i"),
        SchemaMismatch("s"),
        MissingEvidence("m"),
        ReplayInvariantViolation("r"),
        UnsupportedReplay("u"),
    ]

    for f in failures:
        assert isinstance(f, ReplayFailure)