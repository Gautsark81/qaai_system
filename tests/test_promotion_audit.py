# tests/test_promotion_audit.py
import tempfile
import os
from promotion.audit import AuditWriter

def test_audit_write_and_read(tmp_path):
    p = tmp_path / "audit" / "a.jsonl"
    aw = AuditWriter(str(p))
    rec = {"strategy_id": "s1", "decision": "PROMOTE", "reason": "ok"}
    aw.append(rec)
    outs = aw.read_all()
    assert len(outs) == 1
    assert outs[0]["strategy_id"] == "s1"
    # query by strategy
    assert aw.query("s1")[0]["decision"] == "PROMOTE"
