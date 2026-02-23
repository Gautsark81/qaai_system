from core.shadow.runbooks.engine import ShadowRunbookEngine
from core.shadow.runbooks.config import ShadowRunbookConfig


def test_runbook_emits_evidence():
    engine = ShadowRunbookEngine(
        config=ShadowRunbookConfig(enable_shadow_runbooks=True)
    )

    report = engine.execute(runbook="GRACEFUL_HALT")

    assert report.evidence is not None
    assert isinstance(report.evidence, dict)
