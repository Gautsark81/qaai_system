from datetime import datetime
from domain.operator.operator_audit_log import OperatorAuditLog
from domain.operator.operator_action import OperatorAction


def test_operator_audit_log_records():
    log = OperatorAuditLog()
    log.record(
        OperatorAction(
            "admin",
            "PAUSE",
            "STRAT_1",
            "Manual review",
            datetime.utcnow(),
        )
    )
    assert len(log.all()) == 1
