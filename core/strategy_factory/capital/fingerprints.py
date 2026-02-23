from core.evidence.checksum import compute_checksum


def compute_capital_allocation_fingerprint(
    *,
    eligible: bool,
    eligibility_reason: str,
    requested_capital: float,
    max_per_strategy: float,
    global_cap_remaining: float,
    approved_capital: float,
    allocation_reason: str,
) -> str:
    """
    Deterministic fingerprint for capital allocation governance.
    """

    fields = [
        ("eligible", eligible),
        ("eligibility_reason", eligibility_reason),
        ("requested_capital", requested_capital),
        ("max_per_strategy", max_per_strategy),
        ("global_cap_remaining", global_cap_remaining),
        ("approved_capital", approved_capital),
        ("allocation_reason", allocation_reason),
    ]

    return compute_checksum(fields=fields)
