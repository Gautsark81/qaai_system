# core/oversight/correlation/severity_policy.py

from typing import Iterable, List


_ALLOWED = {"INFO", "WARNING", "CRITICAL"}


def compose_severity(
    *,
    severities: Iterable[str],
    involved_domains: Iterable[str],
) -> str:
    """
    Deterministically compose correlated severity.

    Rules (in order of precedence):

    1. Any CRITICAL → CRITICAL
    2. WARNING across ≥2 domains → CRITICAL
    3. Any WARNING → WARNING
    4. Otherwise → INFO

    This function MUST:
    - Be pure
    - Be deterministic
    - Never raise
    """

    severities = list(severities)
    domains = set(involved_domains)

    if not severities:
        return "INFO"

    for s in severities:
        if s not in _ALLOWED:
            # Defensive downgrade, never crash oversight
            return "INFO"

    # Rule 1
    if "CRITICAL" in severities:
        return "CRITICAL"

    # Rule 2
    if severities.count("WARNING") >= 2 and len(domains) >= 2:
        return "CRITICAL"

    # Rule 3
    if "WARNING" in severities:
        return "WARNING"

    # Rule 4
    return "INFO"
