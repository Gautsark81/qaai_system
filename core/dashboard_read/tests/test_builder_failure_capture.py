from core.dashboard_read.builder import SystemSnapshotBuilder


def test_builder_records_failures(monkeypatch):
    """
    D-3 GUARANTEE:
    Builder records failures internally.
    """

    def explode():
        raise ValueError("source missing")

    monkeypatch.setattr(
        "core.dashboard_read.providers.execution.build_execution_state",
        explode,
    )

    builder = SystemSnapshotBuilder(
        execution_mode="paper",
        market_status="open",
        system_version="test",
    )

    builder.build()

    failures = builder.failures

    assert "execution_state" in failures
    assert "ValueError" in failures["execution_state"]
