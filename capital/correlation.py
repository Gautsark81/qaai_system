def apply_correlation_penalty(weight: float, correlated: bool):
    """
    Simple conservative throttle for correlated strategies.
    """
    if correlated:
        return weight * 0.50
    return weight
