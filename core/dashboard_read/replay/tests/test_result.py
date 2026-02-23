from core.dashboard_read.replay.result import (
    ReplayResult,
    ReplayDiscrepancy,
    ReplayWarning,
)


def test_clean_replay_result():
    result = ReplayResult(
        replay_id="r1",
        snapshot_hash="abc",
        chain_hash="def",
        verification_status=True,
    )

    assert result.is_clean is True
    assert result.discrepancies == []
    assert result.warnings == []


def test_replay_result_with_discrepancy_is_not_clean():
    result = ReplayResult(
        replay_id="r2",
        snapshot_hash="abc",
        chain_hash="def",
        verification_status=True,
        discrepancies=[ReplayDiscrepancy(component="risk", description="Mismatch")],
    )

    assert result.is_clean is False