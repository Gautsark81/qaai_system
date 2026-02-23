from core.shadow.runbooks.engine import ShadowRunbookEngine
from core.shadow.runbooks.config import ShadowRunbookConfig
from core.governance.reconstruction import reconstruct_system_state


def test_runbook_engine_has_no_side_effects():
    engine = ShadowRunbookEngine(
        config=ShadowRunbookConfig(enable_shadow_runbooks=True)
    )

    before = reconstruct_system_state()
    engine.execute("FORCED_SHUTDOWN")
    after = reconstruct_system_state()

    assert before == after
