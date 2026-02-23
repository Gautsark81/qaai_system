def test_governance_view_is_read_only():
    """
    Guardrail test:
    Governance view must not contain approval or execution logic.
    """

    with open(
        "modules/operator_dashboard/views/governance_view.py",
        "r",
    ) as f:
        content = f.read()

    forbidden = [
        "approve(",
        "reject(",
        "save(",
        "can_go_live",
        "admit(",
        "execute",
        "broker",
    ]

    for token in forbidden:
        assert token not in content
