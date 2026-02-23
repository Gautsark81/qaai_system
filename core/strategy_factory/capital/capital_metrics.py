# core/strategy_factory/capital/capital_metrics.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from statistics import variance


# ============================================================
# DATA STRUCTURES
# ============================================================


@dataclass(frozen=True)
class CapitalStabilitySnapshot:
    """
    Immutable capital state snapshot for stability computation.

    This structure must be populated by upstream capital allocator /
    strategy engine. This module performs pure deterministic analysis.
    """

    total_capital: float
    gross_exposure: float
    max_envelope: float

    strategy_capital_allocations: Dict[str, float]
    correlated_exposure: float

    modeled_exposure: Optional[float] = None
    realized_exposure: Optional[float] = None

    throttle_activations: int = 0
    total_execution_cycles: int = 1

    promotions: int = 0
    demotions: int = 0
    total_strategies: int = 1


@dataclass(frozen=True)
class CapitalStabilityMetrics:
    """
    Fully computed capital stability metrics.
    """

    geo: float
    esr: float
    cav: float
    scci: float
    cer: float
    scv: float
    rmed: float
    taf: float


@dataclass(frozen=True)
class CapitalStabilityScore:
    """
    Composite capital stability score (0–100).
    """

    exposure_score: float
    allocation_score: float
    interaction_score: float
    drift_score: float
    governance_score: float
    composite_score: float


# ============================================================
# METRIC COMPUTER
# ============================================================


class CapitalMetricsComputer:
    """
    Deterministic capital stability metric engine.
    """

    @staticmethod
    def compute(
        current: CapitalStabilitySnapshot,
        previous: Optional[CapitalStabilitySnapshot] = None,
    ) -> CapitalStabilityMetrics:

        geo = CapitalMetricsComputer._compute_geo(current, previous)
        esr = CapitalMetricsComputer._compute_esr(current)
        cav = CapitalMetricsComputer._compute_cav(current)
        scci = CapitalMetricsComputer._compute_scci(current)
        cer = CapitalMetricsComputer._compute_cer(current)
        scv = CapitalMetricsComputer._compute_scv(current)
        rmed = CapitalMetricsComputer._compute_rmed(current)
        taf = CapitalMetricsComputer._compute_taf(current)

        return CapitalStabilityMetrics(
            geo=geo,
            esr=esr,
            cav=cav,
            scci=scci,
            cer=cer,
            scv=scv,
            rmed=rmed,
            taf=taf,
        )

    # ========================================================
    # INDIVIDUAL METRICS
    # ========================================================

    @staticmethod
    def _compute_geo(
        current: CapitalStabilitySnapshot,
        previous: Optional[CapitalStabilitySnapshot],
    ) -> float:
        if previous is None or current.total_capital == 0:
            return 0.0

        return abs(current.gross_exposure - previous.gross_exposure) / current.total_capital

    @staticmethod
    def _compute_esr(current: CapitalStabilitySnapshot) -> float:
        if current.max_envelope == 0:
            return 0.0
        return current.gross_exposure / current.max_envelope

    @staticmethod
    def _compute_cav(current: CapitalStabilitySnapshot) -> float:
        allocations = list(current.strategy_capital_allocations.values())
        if len(allocations) <= 1:
            return 0.0
        return variance(allocations)

    @staticmethod
    def _compute_scci(current: CapitalStabilitySnapshot) -> float:
        if current.total_capital == 0:
            return 0.0

        shares = [
            alloc / current.total_capital
            for alloc in current.strategy_capital_allocations.values()
        ]

        return sum(share * share for share in shares)

    @staticmethod
    def _compute_cer(current: CapitalStabilitySnapshot) -> float:
        if current.gross_exposure == 0:
            return 0.0
        return current.correlated_exposure / current.gross_exposure

    @staticmethod
    def _compute_scv(current: CapitalStabilitySnapshot) -> float:
        if current.total_strategies == 0:
            return 0.0

        churn = current.promotions + current.demotions
        return churn / current.total_strategies

    @staticmethod
    def _compute_rmed(current: CapitalStabilitySnapshot) -> float:
        if (
            current.modeled_exposure is None
            or current.realized_exposure is None
            or current.modeled_exposure == 0
        ):
            return 0.0

        return abs(current.realized_exposure - current.modeled_exposure) / current.modeled_exposure

    @staticmethod
    def _compute_taf(current: CapitalStabilitySnapshot) -> float:
        if current.total_execution_cycles == 0:
            return 0.0

        return current.throttle_activations / current.total_execution_cycles


# ============================================================
# STABILITY SCORE CALCULATOR
# ============================================================


class StabilityScoreCalculator:
    """
    Converts raw metrics into weighted stability score (0–100).
    """

    # Category weights (must match governance doc)
    EXPOSURE_WEIGHT = 0.25
    ALLOCATION_WEIGHT = 0.20
    INTERACTION_WEIGHT = 0.20
    DRIFT_WEIGHT = 0.20
    GOVERNANCE_WEIGHT = 0.15

    @staticmethod
    def compute(metrics: CapitalStabilityMetrics) -> CapitalStabilityScore:

        exposure_score = StabilityScoreCalculator._score_exposure(metrics)
        allocation_score = StabilityScoreCalculator._score_allocation(metrics)
        interaction_score = StabilityScoreCalculator._score_interaction(metrics)
        drift_score = StabilityScoreCalculator._score_drift(metrics)
        governance_score = StabilityScoreCalculator._score_governance(metrics)

        composite = (
            exposure_score * StabilityScoreCalculator.EXPOSURE_WEIGHT
            + allocation_score * StabilityScoreCalculator.ALLOCATION_WEIGHT
            + interaction_score * StabilityScoreCalculator.INTERACTION_WEIGHT
            + drift_score * StabilityScoreCalculator.DRIFT_WEIGHT
            + governance_score * StabilityScoreCalculator.GOVERNANCE_WEIGHT
        )

        return CapitalStabilityScore(
            exposure_score=exposure_score,
            allocation_score=allocation_score,
            interaction_score=interaction_score,
            drift_score=drift_score,
            governance_score=governance_score,
            composite_score=round(composite, 2),
        )

    # ========================================================
    # CATEGORY SCORERS (bounded linear transforms)
    # ========================================================

    @staticmethod
    def _bounded_score(value: float, ideal_max: float) -> float:
        if value <= ideal_max:
            return 100.0
        if value >= ideal_max * 2:
            return 0.0
        return 100.0 * (1 - (value - ideal_max) / ideal_max)

    @staticmethod
    def _score_exposure(m: CapitalStabilityMetrics) -> float:
        geo_score = StabilityScoreCalculator._bounded_score(m.geo, 0.20)
        esr_score = StabilityScoreCalculator._bounded_score(abs(m.esr - 0.65), 0.20)
        return (geo_score + esr_score) / 2

    @staticmethod
    def _score_allocation(m: CapitalStabilityMetrics) -> float:
        cav_score = StabilityScoreCalculator._bounded_score(m.cav, 0.10)
        scci_score = StabilityScoreCalculator._bounded_score(m.scci, 0.25)
        return (cav_score + scci_score) / 2

    @staticmethod
    def _score_interaction(m: CapitalStabilityMetrics) -> float:
        cer_score = StabilityScoreCalculator._bounded_score(m.cer, 0.35)
        scv_score = StabilityScoreCalculator._bounded_score(m.scv, 0.10)
        return (cer_score + scv_score) / 2

    @staticmethod
    def _score_drift(m: CapitalStabilityMetrics) -> float:
        return StabilityScoreCalculator._bounded_score(m.rmed, 0.05)

    @staticmethod
    def _score_governance(m: CapitalStabilityMetrics) -> float:
        return StabilityScoreCalculator._bounded_score(m.taf, 0.05)