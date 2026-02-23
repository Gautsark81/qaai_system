from core.shadow.runbooks.engine import ShadowRunbookEngine
from core.shadow.runbooks.config import ShadowRunbookConfig


def test_runbook_has_no_execution_or_capital_authority():
    engine = ShadowRunbookEngine(
        config=ShadowRunbookConfig(enable_shadow_runbooks=True)
    )

    report = engine.execute("FORCED_SHUTDOWN")

    assert report.has_execution_authority is False
    assert report.has_capital_authority is False
