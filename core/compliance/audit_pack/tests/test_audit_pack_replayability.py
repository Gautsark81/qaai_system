from core.compliance.audit_pack.builder import AuditPackBuilder
from core.execution.replay.engine import ReplayEngine


def test_audit_pack_is_replayable():
    pack = AuditPackBuilder().build()

    engine = ReplayEngine.from_audit_pack(pack)

    assert engine is not None
