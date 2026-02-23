def capital_ramp(day: int) -> float:
    """
    Progressive capital exposure.
    """
    if day < 5:
        return 0.10
    if day < 15:
        return 0.50
    return 1.00
