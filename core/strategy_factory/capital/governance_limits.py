from core.strategy_factory.capital.governance_models import (
    CapitalGovernanceDecision,
    CapitalGovernanceLimits,
)


def decide_capital_governance_limits(
    *,
    strategy_dna: str,
    requested_capital: float,
    strategy_current_capital: float,
    global_capital_used: float,
    limits: CapitalGovernanceLimits,
) -> CapitalGovernanceDecision:
    """
    Enforce hard capital governance limits.

    RULE PRECEDENCE (CRITICAL):
    1. Global cap
    2. Concentration limit
    3. Per-strategy cap
    """

    projected_strategy = strategy_current_capital + requested_capital
    projected_global = global_capital_used + requested_capital

    # --------------------------------------------------
    # 1️⃣ Global capital cap (absolute)
    # --------------------------------------------------
    if projected_global > limits.global_cap:
        return CapitalGovernanceDecision(
            allowed=False,
            reason=(
                f"Global cap exceeded: "
                f"{projected_global:.2f} > {limits.global_cap:.2f}"
            ),
        )

    # --------------------------------------------------
    # 2️⃣ Concentration limit (systemic risk)
    # --------------------------------------------------
    if limits.global_cap > 0:
        concentration = projected_strategy / limits.global_cap
        if concentration > limits.max_concentration_pct:
            return CapitalGovernanceDecision(
                allowed=False,
                reason=(
                    f"Concentration limit exceeded for {strategy_dna}: "
                    f"{concentration:.2%} > {limits.max_concentration_pct:.2%}"
                ),
            )

    # --------------------------------------------------
    # 3️⃣ Per-strategy cap (fairness)
    # --------------------------------------------------
    if projected_strategy > limits.max_per_strategy:
        return CapitalGovernanceDecision(
            allowed=False,
            reason=(
                f"Per-strategy cap exceeded for {strategy_dna}: "
                f"{projected_strategy:.2f} > {limits.max_per_strategy:.2f}"
            ),
        )

    return CapitalGovernanceDecision(
        allowed=True,
        reason="Governance allowed: all checks passed",
    )
