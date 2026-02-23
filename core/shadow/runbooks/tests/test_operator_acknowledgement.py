from core.shadow.runbooks.engine import ShadowRunbookEngine
from core.shadow.runbooks.config import ShadowRunbookConfig


def test_operator_acknowledgement_required():
    engine = ShadowRunbookEngine(
        config=ShadowRunbookConfig(enable_shadow_runbooks=True)
    )

    report = engine.execute(
        runbook="FORCED_SHUTDOWN",
        operator_ack=True,
    )

    assert report.operator_acknowledged is True
