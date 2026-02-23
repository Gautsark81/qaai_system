from core.shadow.runbooks.engine import ShadowRunbookEngine
from core.shadow.runbooks.config import ShadowRunbookConfig
from core.shadow.runbooks.models import RunbookEvent


def test_forced_shutdown_runbook():
    engine = ShadowRunbookEngine(
        config=ShadowRunbookConfig(enable_shadow_runbooks=True)
    )

    report = engine.execute(
        runbook="FORCED_SHUTDOWN"
    )

    assert report.executed is True
    assert RunbookEvent.FORCED_SHUTDOWN in report.events
