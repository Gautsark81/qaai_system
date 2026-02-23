"""
Canonical read interface for capital state.
Used by dashboard snapshot only.
READ-ONLY. NO LOGIC.
"""

def read_capital_metrics():
    """
    Returns an object with capital attributes.
    In production, this should be wired to the
    authoritative capital snapshot producer.
    """

    # IMPORTANT:
    # Do not import deep internals here.
    # This function is intentionally shallow and patchable.

    raise RuntimeError(
        "read_capital_metrics() must be provided by runtime wiring"
    )
