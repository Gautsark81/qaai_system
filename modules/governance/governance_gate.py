from datetime import datetime
from modules.governance.approval_store import ApprovalStore
from modules.governance.capital_envelope import (
    CapitalEnvelope,
    CapitalEnvelopeValidator,
)


class GovernanceGate:
    def __init__(self):
        self.approvals = ApprovalStore()
        self.capital_validator = CapitalEnvelopeValidator()

    def can_go_live(
        self,
        strategy_id: str,
        requested_capital: float,
        envelope: CapitalEnvelope,
        now: datetime,
    ) -> bool:
        if not self.approvals.is_approved(strategy_id, now):
            return False

        if not self.capital_validator.validate(
            requested_capital, envelope
        ):
            return False

        return True
