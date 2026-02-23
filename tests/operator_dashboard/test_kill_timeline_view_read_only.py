def test_kill_timeline_view_is_read_only():
    """
    Guardrail test:
    Kill timeline view must not contain revive or execution logic.
    """

    with open(
        "modules/operator_dashboard/views/kill_timeline_view.py",
        "r",
    ) as f:
        content = f.read()

    forbidden = [
        "revive(",
        "restart(",
        "approve(",
        "admit(",
        "execute(",
        "broker",
        "Order(",
        "OrderManager",
    ]

    for token in forbidden:
        assert token not in content
