from modules.capital.decision import CapitalDecision


def test_capital_decision_cannot_increase_exposure():
    decision = CapitalDecision(
        approved=True,
        max_notional=100_000,
        scale_factor=1.2,
        reason="Invalid scaling",
    )

    assert decision.is_scaling_only() is False
