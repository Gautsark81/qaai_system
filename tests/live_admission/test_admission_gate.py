from datetime import datetime
from modules.live_admission.admission_gate import LiveAdmissionGate
from modules.governance.governance_gate import GovernanceGate
from modules.governance.approval import ApprovalService
from modules.governance.capital_envelope import CapitalEnvelope


def test_live_admission_success():
    gate = GovernanceGate()
    svc = ApprovalService()

    record = svc.approve("s1", "admin", "approved")
    gate.approvals.save(record)

    admission = LiveAdmissionGate(gate).admit(
        strategy_id="s1",
        capital=500_000,
        envelope=CapitalEnvelope(1_000_000, 20_000),
        token_issued_at=datetime.utcnow(),
        now=datetime.utcnow(),
    )

    assert admission is not None
    assert admission.strategy_id == "s1"


def test_live_admission_blocked_without_approval():
    gate = GovernanceGate()

    admission = LiveAdmissionGate(gate).admit(
        strategy_id="s1",
        capital=500_000,
        envelope=CapitalEnvelope(1_000_000, 20_000),
        token_issued_at=datetime.utcnow(),
        now=datetime.utcnow(),
    )

    assert admission is None
