from datetime import datetime, timedelta
from modules.governance.governance_gate import GovernanceGate
from modules.live_admission.admission_record import LiveAdmissionRecord
from modules.live_admission.token_guard import TokenSessionGuard
from modules.governance.capital_envelope import CapitalEnvelope


class LiveAdmissionGate:
    def __init__(self, governance_gate: GovernanceGate):
        self.governance_gate = governance_gate

    def admit(
        self,
        strategy_id: str,
        capital: float,
        envelope: CapitalEnvelope,
        token_issued_at: datetime,
        now: datetime,
        admission_hours: int = 6,
    ) -> LiveAdmissionRecord | None:

        token_guard = TokenSessionGuard(token_issued_at)

        if not token_guard.is_valid(now):
            return None

        if not self.governance_gate.can_go_live(
            strategy_id=strategy_id,
            requested_capital=capital,
            envelope=envelope,
            now=now,
        ):
            return None

        return LiveAdmissionRecord(
            strategy_id=strategy_id,
            capital=capital,
            admitted_at=now,
            expires_at=now + timedelta(hours=admission_hours),
            token_session_id=f"token@{token_issued_at.isoformat()}",
        )
