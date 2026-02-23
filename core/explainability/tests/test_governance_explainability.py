from core.explainability.governance_explainer import GovernanceExplainer


def test_governance_explanation_references_rules():
    explainer = GovernanceExplainer()

    explanation = explainer.explain(
        allowed=False,
        rule="KILL_SWITCH_ACTIVE",
        phase="Phase 22",
    )

    assert "denied" in explanation.lower()
    assert "KILL_SWITCH_ACTIVE" in explanation
    assert "Phase 22" in explanation
