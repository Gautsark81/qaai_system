def test_live_admission_view_is_read_only():
    """
    Guardrail test:
    Live admission view must not contain admission or execution logic.
    """

    with open(
        "modules/operator_dashboard/views/live_admission_view.py",
        "r",
    ) as f:
        content = f.read()

    forbidden = [
        "admit(",
        "re_admit",
        "can_go_live",
        "approve(",
        "execute(",
        "broker",
        "Order(",
        "OrderManager",
    ]

    for token in forbidden:
        assert token not in content
