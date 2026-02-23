def test_policy_feedback_view_is_read_only():
    """
    Guardrail test:
    Policy feedback panel must not modify governance or execution.
    """

    with open(
        "modules/operator_dashboard/views/policy_feedback_view.py",
        "r",
    ) as f:
        content = f.read()

    forbidden = [
        "apply(",
        "update(",
        "set_",
        "approve(",
        "admit(",
        "execute(",
        "broker",
        "Order(",
        "OrderManager",
    ]

    for token in forbidden:
        assert token not in content
