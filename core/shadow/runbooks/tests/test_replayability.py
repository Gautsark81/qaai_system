from core.shadow.runbooks.engine import ShadowRunbookEngine
from core.shadow.runbooks.config import ShadowRunbookConfig


def test_runbook_replayability():
    engine = ShadowRunbookEngine(
        config=ShadowRunbookConfig(enable_shadow_runbooks=True)
    )

    r1 = engine.execute("GRACEFUL_HALT")
    r2 = engine.execute("GRACEFUL_HALT")

    assert r1 == r2
