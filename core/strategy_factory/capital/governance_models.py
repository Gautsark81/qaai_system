from dataclasses import dataclass


# ==========================================================
# Capital Governance Limits (PUBLIC CONTRACT)
# ==========================================================

@dataclass(frozen=True)
class CapitalGovernanceLimits:
    """
    Hard capital governance limits.

    Supports BOTH legacy and current naming:
    - per_strategy_cap  (legacy)
    - max_per_strategy  (current)

    Internally normalized to max_per_strategy.
    """

    global_cap: float
    max_per_strategy: float
    max_concentration_pct: float

    def __init__(
        self,
        *,
        global_cap: float,
        max_concentration_pct: float,
        per_strategy_cap: float | None = None,
        max_per_strategy: float | None = None,
    ):
        # -------------------------------
        # Resolve strategy cap
        # -------------------------------
        if max_per_strategy is None and per_strategy_cap is None:
            raise TypeError(
                "One of 'max_per_strategy' or 'per_strategy_cap' must be provided"
            )

        resolved_cap = (
            max_per_strategy
            if max_per_strategy is not None
            else per_strategy_cap
        )

        if resolved_cap is None:
            raise ValueError("Strategy cap could not be resolved")

        # -------------------------------
        # Assign (frozen dataclass)
        # -------------------------------
        object.__setattr__(self, "global_cap", global_cap)
        object.__setattr__(self, "max_per_strategy", resolved_cap)
        object.__setattr__(self, "max_concentration_pct", max_concentration_pct)

        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.global_cap, (int, float)) or self.global_cap <= 0:
            raise ValueError("global_cap must be a positive number")

        if not isinstance(self.max_per_strategy, (int, float)) or self.max_per_strategy <= 0:
            raise ValueError("max_per_strategy must be a positive number")

        if not isinstance(self.max_concentration_pct, (int, float)):
            raise ValueError("max_concentration_pct must be numeric")

        if not (0 < self.max_concentration_pct <= 1):
            raise ValueError("max_concentration_pct must be in (0, 1]")

    # --------------------------------------------------
    # Backward-compatibility alias (READ-ONLY)
    # --------------------------------------------------
    @property
    def per_strategy_cap(self) -> float:
        """
        Legacy alias for max_per_strategy.

        ⚠ Do NOT remove until all call sites are migrated.
        """
        return self.max_per_strategy


# ==========================================================
# Capital Governance Decision (OUTPUT CONTRACT)
# ==========================================================

@dataclass(frozen=True)
class CapitalGovernanceDecision:
    """
    Result of capital governance evaluation.
    """

    allowed: bool
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.allowed, bool):
            raise TypeError("allowed must be a boolean")

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
