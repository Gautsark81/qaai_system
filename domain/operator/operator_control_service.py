from datetime import datetime
from domain.operator.operator_action import OperatorAction
from domain.operator.operator_command_gate import OperatorCommandGate
from domain.operator.operator_audit_log import OperatorAuditLog


class OperatorControlService:
    """
    Wires UI commands → audit trail.
    """

    def __init__(self, audit_log: OperatorAuditLog):
        self.audit_log = audit_log

    def submit(
        self,
        operator_id: str,
        action: str,
        target: str,
        reason: str,
    ) -> bool:

        if not OperatorCommandGate.allow(action):
            return False

        self.audit_log.record(
            OperatorAction(
                operator_id=operator_id,
                action=action,
                target=target,
                reason=reason,
                timestamp=datetime.utcnow(),
            )
        )
        return True
