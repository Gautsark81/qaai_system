from typing import Dict, List

from .models import AllocationResult
from .snapshot import EnsembleSnapshot
from .meta_alpha import MetaAlphaCalculator
from .regime_adjustment import RegimeAdjustmentEngine

# Productivity Integration
from core.strategy_factory.capital.productivity.productivity_model import (
    compute_productivity_snapshot,
)
from core.strategy_factory.capital.productivity_integration import (
    compute_productivity_rotation_map,
)
from core.strategy_factory.capital.productivity.memory import (
    ProductivityMemory,
)

# Deterministic module-level memory (replay-safe within process)
_productivity_memory = ProductivityMemory()


class EnsembleAllocator:

    @staticmethod
    def _tier_weight(ssr: float) -> int:
        if ssr >= 90:
            return 3
        elif ssr >= 85:
            return 2
        elif ssr >= 80:
            return 1
        else:
            return 0

    @staticmethod
    def _drawdown_multiplier(drawdown_pct: float) -> float:
        if drawdown_pct <= 5:
            return 1.0
        elif drawdown_pct <= 10:
            return 0.75
        elif drawdown_pct <= 20:
            return 0.5
        else:
            return 0.25

    @staticmethod
    def allocate(snapshot: EnsembleSnapshot) -> AllocationResult:

        strategies = snapshot.strategies

        tier_weights: Dict[str, int] = {}
        drawdown_multipliers: Dict[str, float] = {}
        suspensions: Dict[str, str] = {}
        base_weights: Dict[str, float] = {}

        # --------------------------------------------------
        # STEP 1 — Suspension + Base Weight
        # --------------------------------------------------
        for s in strategies:

            if s.drawdown_pct > snapshot.suspension_drawdown_pct:
                suspensions[s.strategy_id] = "DRAW_DOWN_BREACH"
                base_weights[s.strategy_id] = 0.0
                continue

            if s.ssr < snapshot.suspension_min_ssr:
                suspensions[s.strategy_id] = "SSR_BELOW_THRESHOLD"
                base_weights[s.strategy_id] = 0.0
                continue

            tier = EnsembleAllocator._tier_weight(s.ssr)
            mult = EnsembleAllocator._drawdown_multiplier(s.drawdown_pct)

            tier_weights[s.strategy_id] = tier
            drawdown_multipliers[s.strategy_id] = mult
            base_weights[s.strategy_id] = tier * mult

        active_weights = {
            sid: w
            for sid, w in base_weights.items()
            if sid not in suspensions and w > 0
        }

        if not active_weights:
            return AllocationResult(
                allocations={},
                tier_weights=tier_weights,
                drawdown_multipliers=drawdown_multipliers,
                suspensions=suspensions,
                governance_adjustments={},
                snapshot_hash=snapshot.snapshot_hash,
            )

        # --------------------------------------------------
        # STEP 2 — Diversity (placeholder)
        # --------------------------------------------------
        diversity_weights = {
            sid: w * (1 - 0.0 * snapshot.diversity_penalty_strength)
            for sid, w in active_weights.items()
        }

        # --------------------------------------------------
        # STEP 3 — Regime Adjustment
        # --------------------------------------------------
        regime_params = RegimeAdjustmentEngine.adjust(snapshot)

        adjusted_decay_strength = regime_params.adjusted_decay_strength
        adjusted_reinforcement_strength = (
            regime_params.adjusted_reinforcement_strength
        )

        # --------------------------------------------------
        # STEP 4 — Decay Suppression
        # --------------------------------------------------
        decay_weights: Dict[str, float] = {}

        for sid, weight in diversity_weights.items():
            decay_score = snapshot.decay_scores.get(sid, 0.0)
            penalty_multiplier = 1 - (decay_score * adjusted_decay_strength)
            penalty_multiplier = max(0.0, penalty_multiplier)
            decay_weights[sid] = weight * penalty_multiplier

        total_weight = sum(decay_weights.values())

        if total_weight == 0:
            return AllocationResult(
                allocations={},
                tier_weights=tier_weights,
                drawdown_multipliers=drawdown_multipliers,
                suspensions=suspensions,
                governance_adjustments={},
                snapshot_hash=snapshot.snapshot_hash,
            )

        # --------------------------------------------------
        # STEP 5 — Provisional Allocation
        # --------------------------------------------------
        provisional_allocations = {
            sid: (w / total_weight) * snapshot.available_capital
            for sid, w in decay_weights.items()
        }

        temp_result = AllocationResult(
            allocations=provisional_allocations,
            tier_weights=tier_weights,
            drawdown_multipliers=drawdown_multipliers,
            suspensions=suspensions,
            governance_adjustments={sid: 0.0 for sid in provisional_allocations},
            snapshot_hash=snapshot.snapshot_hash,
        )

        meta = MetaAlphaCalculator.calculate(snapshot, temp_result)
        avg_score = sum(meta.scores.values()) / len(meta.scores)

        # --------------------------------------------------
        # STEP 6 — Meta Tilt + Regime Reinforcement
        # --------------------------------------------------
        tilted_weights: Dict[str, float] = {}

        for sid, weight in decay_weights.items():

            score = meta.scores.get(sid, 0.0)

            tilt_multiplier = 1 + (score - avg_score) * 0.1

            reinforcement_boost = 1 + (
                max(0.0, score - avg_score)
                * adjusted_reinforcement_strength
                * 0.1
            )

            final_multiplier = tilt_multiplier * reinforcement_boost
            final_multiplier = max(0.85, min(1.15, final_multiplier))

            tilted_weights[sid] = weight * final_multiplier

        total_tilted_weight = sum(tilted_weights.values())

        # --------------------------------------------------
        # STEP 7 — Allocation + Governance Caps
        # --------------------------------------------------
        allocations: Dict[str, float] = {}
        governance_adjustments: Dict[str, float] = {}

        for sid, weight in tilted_weights.items():
            normalized = weight / total_tilted_weight
            allocation = normalized * snapshot.available_capital
            original = allocation

            allocation = min(allocation, snapshot.per_strategy_cap)
            allocation = min(allocation, snapshot.concentration_cap)

            allocations[sid] = allocation
            governance_adjustments[sid] = original - allocation

        for sid in suspensions:
            allocations[sid] = 0.0
            governance_adjustments[sid] = 0.0

        # --------------------------------------------------
        # STEP 7.5 — Productivity Rotation with Memory
        # --------------------------------------------------
        productivity_snapshots: List = []

        for s in strategies:
            if s.strategy_id in allocations and allocations[s.strategy_id] > 0:

                snap = compute_productivity_snapshot(
                    strategy_dna=s.strategy_id,
                    net_return=s.ssr,  # deterministic proxy
                    avg_allocated_capital=max(1.0, allocations[s.strategy_id]),
                    max_drawdown=s.drawdown_pct,
                    regime_confidence=1.0,
                )
                productivity_snapshots.append(snap)

        rotation_map = compute_productivity_rotation_map(productivity_snapshots)

        # Apply memory stabilization (hysteresis)
        stabilized_rotation_map = _productivity_memory.update(rotation_map)

        for sid in allocations:
            multiplier = stabilized_rotation_map.get(sid, 1.0)
            allocations[sid] *= multiplier

        # Renormalize after productivity
        total_after_productivity = sum(allocations.values())
        if total_after_productivity > 0:
            scale = snapshot.available_capital / total_after_productivity
            for sid in allocations:
                allocations[sid] *= scale

        # --------------------------------------------------
        # STEP 8 — Global Cap Enforcement
        # --------------------------------------------------
        total_allocated = sum(allocations.values())

        if total_allocated > snapshot.global_cap:
            scale_factor = snapshot.global_cap / total_allocated
            for sid in allocations:
                original = allocations[sid]
                allocations[sid] *= scale_factor
                governance_adjustments[sid] += original - allocations[sid]

        return AllocationResult(
            allocations=allocations,
            tier_weights=tier_weights,
            drawdown_multipliers=drawdown_multipliers,
            suspensions=suspensions,
            governance_adjustments=governance_adjustments,
            snapshot_hash=snapshot.snapshot_hash,
        )