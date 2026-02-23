from domain.operator.operator_control_service import (
    OperatorControlService
)
from domain.operator.operator_audit_log import OperatorAuditLog


def test_operator_control_service_accepts_kill():
    svc = OperatorControlService(OperatorAuditLog())
    ok = svc.submit(
        operator_id="admin",
        action="KILL",
        target="SYSTEM",
        reason="Emergency stop",
    )
    assert ok is True
