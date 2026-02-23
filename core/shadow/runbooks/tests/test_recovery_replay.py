from core.shadow.runbooks.engine import ShadowRunbookEngine
from core.shadow.runbooks.config import ShadowRunbookConfig


def test_recovery_runbook_replayable():
    engine = ShadowRunbookEngine(
        config=ShadowRunbookConfig(enable_shadow_runbooks=True)
    )

    r1 = engine.execute(runbook="RECOVERY_REPLAY")
    r2 = engine.execute(runbook="RECOVERY_REPLAY")

    assert r1 == r2
