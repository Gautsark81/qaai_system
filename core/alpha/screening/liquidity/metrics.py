def compute_order_pct_adv(order_value: float, adv_value: float) -> float:
    return order_value / adv_value


def compute_exit_days(order_pct_adv: float, volatility_spike: bool) -> float:
    """
    Extremely conservative placeholder:
    - Stress doubles exit time
    """
    base_days = order_pct_adv * 10
    return base_days * 2 if volatility_spike else base_days
