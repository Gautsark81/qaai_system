from __future__ import annotations


class PromotionIntelligenceReplayMismatch(Exception):
    """
    Raised when deterministic replay of Promotion Intelligence
    fails to reproduce the expected trace hash.

    This indicates:
    - Drift in promotion intelligence logic
    - Non-deterministic behavior
    - Modified inputs
    - Version skew between artifacts
    """

    pass