from core.shadow.runbooks.engine import ShadowRunbookEngine
from core.shadow.runbooks.config import ShadowRunbookConfig
from core.shadow.runbooks.models import RunbookEvent


def test_graceful_halt_runbook():
    engine = ShadowRunbookEngine(
        config=ShadowRunbookConfig(enable_shadow_runbooks=True)
    )

    report = engine.execute(
        runbook="GRACEFUL_HALT"
    )

    assert report.executed is True
    assert RunbookEvent.GRACEFUL_HALT in report.events
