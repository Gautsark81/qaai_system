from core.capital.governance.approval import CapitalGovernanceGate


def test_governance_blocks_on_risk_breach():
    gate = CapitalGovernanceGate()

    decision = gate.evaluate(
        strategy_dna="dna123",
        stress_breach=True,
        concentration_breach=False,
    )

    assert decision.decision == "BLOCK"
    assert decision.approved_by is None


def test_governance_requires_operator_when_clean():
    gate = CapitalGovernanceGate()

    decision = gate.evaluate(
        strategy_dna="dna123",
        stress_breach=False,
        concentration_breach=False,
    )

    assert decision.decision == "ESCALATE"


def test_governance_approves_with_operator():
    gate = CapitalGovernanceGate()

    decision = gate.evaluate(
        strategy_dna="dna123",
        stress_breach=False,
        concentration_breach=False,
        operator="CIO",
    )

    assert decision.decision == "APPROVE"
    assert decision.approved_by == "CIO"
