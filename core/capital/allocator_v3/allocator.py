from typing import Dict, List

from core.capital.allocator_v3.contracts import (
    StrategyCapitalProfile,
    StrategyDecision,
    CapitalDecisionArtifact,
    CapitalDecisionStatus,
    AllocationValue,
    CapitalAttribution,
)
from core.strategy_factory.fitness.contracts import FitnessResult
from core.regime.taxonomy import MarketRegime


class CapitalAllocatorV3:
    """
    Canonical capital allocator (V3).

    Guarantees:
    - Deterministic allocation
    - Explicit constraint attribution
    - No side effects
    - No evidence emission (pure decision engine)
    """

    REGIME_THROTTLE = {
        MarketRegime.TREND_LOW_VOL: 1.0,
        MarketRegime.TREND_HIGH_VOL: 0.7,
        MarketRegime.RANGE_LOW_VOL: 0.6,
        MarketRegime.RANGE_HIGH_VOL: 0.4,
        MarketRegime.CHAOTIC: 0.2,
    }

    def allocate(
        self,
        profiles: List[StrategyCapitalProfile],
        fitness: Dict[str, FitnessResult],
        regime: MarketRegime,
    ) -> CapitalDecisionArtifact:

        allocations: Dict[str, AllocationValue] = {}
        decisions: Dict[str, StrategyDecision] = {}
        attribution: Dict[str, CapitalAttribution] = {}

        throttle = self.REGIME_THROTTLE.get(regime, 1.0)
        total_allocated = 0.0

        # ==================================================
        # Per-strategy allocation
        # ==================================================
        for profile in profiles:
            fit = fitness.get(profile.strategy_id)
            constraints: List[str] = []

            if not fit:
                constraints.append("missing_fitness")

            if fit and not fit.is_capital_eligible:
                constraints.append("not_capital_eligible")

            if fit and fit.raw_fitness < profile.min_fitness:
                constraints.append("below_min_fitness")

            # --------------------------------------------------
            # 🚫 Blocked strategy
            # --------------------------------------------------
            if not fit or constraints:
                allocations[profile.strategy_id] = AllocationValue(0.0)

                decisions[profile.strategy_id] = StrategyDecision(
                    strategy_id=profile.strategy_id,
                    raw_fitness=fit.raw_fitness if fit else 0.0,
                    fragility_penalty=fit.fragility_penalty if fit else 0.0,
                    final_allocation=0.0,
                    regime=regime,
                    reasons=fit.reasons if fit else ["No fitness"],
                    is_capital_eligible=False,
                )

                attribution[profile.strategy_id] = CapitalAttribution(
                    strategy_id=profile.strategy_id,
                    final_allocation=0.0,
                    applied_constraints=constraints,
                    raw_fitness=fit.raw_fitness if fit else 0.0,
                    fragility_penalty=fit.fragility_penalty if fit else 0.0,
                    regime_throttle=throttle,
                    final_weight=0.0,
                )
                continue

            # --------------------------------------------------
            # ✅ Eligible strategy
            # --------------------------------------------------
            alloc = profile.max_allocation

            alloc *= (1.0 - fit.fragility_penalty)
            if fit.fragility_penalty > 0:
                constraints.append("fragility_penalty")

            alloc *= throttle
            if throttle < 1.0:
                constraints.append("regime_throttle")

            alloc = round(alloc, 4)

            allocations[profile.strategy_id] = AllocationValue(alloc)

            decisions[profile.strategy_id] = StrategyDecision(
                strategy_id=profile.strategy_id,
                raw_fitness=fit.raw_fitness,
                fragility_penalty=fit.fragility_penalty,
                final_allocation=alloc,
                regime=regime,
                reasons=fit.reasons,
                is_capital_eligible=True,
            )

            attribution[profile.strategy_id] = CapitalAttribution(
                strategy_id=profile.strategy_id,
                final_allocation=alloc,
                applied_constraints=constraints,
                raw_fitness=fit.raw_fitness,
                fragility_penalty=fit.fragility_penalty,
                regime_throttle=throttle,
                final_weight=alloc,
            )

            total_allocated += alloc

        # ==================================================
        # ⚖️ Hard-cap normalization (portfolio ≤ 1.0)
        # ==================================================
        if total_allocated > 1.0:
            scale = round(1.0 / total_allocated, 6)
            total_allocated = 0.0

            for sid, value in allocations.items():
                scaled = round(value.allocated_fraction * scale, 4)
                allocations[sid] = AllocationValue(scaled)

                a = attribution[sid]
                attribution[sid] = CapitalAttribution(
                    strategy_id=a.strategy_id,
                    final_allocation=scaled,
                    applied_constraints=a.applied_constraints + ["scaled_to_fit_cap"],
                    raw_fitness=a.raw_fitness,
                    fragility_penalty=a.fragility_penalty,
                    regime_throttle=a.regime_throttle,
                    final_weight=scaled,
                )

                d = decisions[sid]
                decisions[sid] = StrategyDecision(
                    strategy_id=d.strategy_id,
                    raw_fitness=d.raw_fitness,
                    fragility_penalty=d.fragility_penalty,
                    final_allocation=scaled,
                    regime=d.regime,
                    reasons=d.reasons,
                    is_capital_eligible=d.is_capital_eligible,
                )

                total_allocated += scaled

        # ==================================================
        # 🧭 Final status
        # ==================================================
        status = (
            CapitalDecisionStatus.BLOCKED
            if total_allocated == 0.0
            else CapitalDecisionStatus.THROTTLED
            if throttle < 1.0
            else CapitalDecisionStatus.APPROVED
        )

        return CapitalDecisionArtifact(
            allocations=allocations,
            decisions=decisions,
            attribution=attribution,
            total_allocated=round(total_allocated, 4),
            status=status,
        )
