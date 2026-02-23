from typing import List


def load_symbol_universe() -> List[str]:
    """
    Deterministic universe snapshot.

    Later versions may load from:
    - NSE master
    - Index constituents
    - Operator-defined lists
    """
    return [
        "RELIANCE",
        "INFY",
        "TCS",
        "HDFCBANK",
        "ICICIBANK",
        "SBIN",
        "LT",
    ]
