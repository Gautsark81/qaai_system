def test_dashboard_is_read_only():
    """
    The dashboard must not import execution or approval modules.
    This test is a guardrail against future regressions.
    """

    with open(
        "modules/operator_dashboard/dashboard_app.py", "r"
    ) as f:
        content = f.read()

    forbidden = [
        "Execution",
        "Order",
        "Broker",
        "approve(",
        "admit(",
        "can_go_live",
    ]

    for token in forbidden:
        assert token not in content
