from core.shadow.runbooks.engine import ShadowRunbookEngine
from core.shadow.runbooks.config import ShadowRunbookConfig


def test_runbook_engine_disabled_by_default():
    engine = ShadowRunbookEngine()
    assert engine.is_enabled is False


def test_runbook_engine_requires_explicit_enable():
    engine = ShadowRunbookEngine(
        config=ShadowRunbookConfig()
    )
    assert engine.is_enabled is False


def test_runbook_engine_enables_with_flag():
    engine = ShadowRunbookEngine(
        config=ShadowRunbookConfig(enable_shadow_runbooks=True)
    )
    assert engine.is_enabled is True
