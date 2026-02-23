from core.shadow.runbooks.engine import ShadowRunbookEngine
from core.shadow.runbooks.config import ShadowRunbookConfig


def test_runbook_engine_deterministic():
    config = ShadowRunbookConfig(enable_shadow_runbooks=True)

    engine_1 = ShadowRunbookEngine(config=config)
    engine_2 = ShadowRunbookEngine(config=config)

    assert engine_1.execute("FORCED_SHUTDOWN") == engine_2.execute("FORCED_SHUTDOWN")
