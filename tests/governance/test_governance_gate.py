from datetime import datetime
from modules.governance.governance_gate import GovernanceGate
from modules.governance.approval import ApprovalService
from modules.governance.capital_envelope import CapitalEnvelope


def test_governance_gate_allows():
    gate = GovernanceGate()
    svc = ApprovalService()

    record = svc.approve("s1", "admin", "ok")
    gate.approvals.save(record)

    env = CapitalEnvelope(max_capital=1_000_000, max_daily_loss=20_000)

    assert gate.can_go_live(
        "s1", 500_000, env, datetime.utcnow()
    )


def test_governance_gate_blocks_no_approval():
    gate = GovernanceGate()

    env = CapitalEnvelope(max_capital=1_000_000, max_daily_loss=20_000)

    assert not gate.can_go_live(
        "s1", 500_000, env, datetime.utcnow()
    )
