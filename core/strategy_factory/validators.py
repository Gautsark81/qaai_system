from typing import Set, List

from core.strategy_factory.dna import AlphaGenome
from core.strategy_factory.exceptions import StrategyValidationError


# ======================================================
# Canonical Registries (V3.2.2)
# ======================================================

ALLOWED_SIGNALS: Set[str] = {
    "momentum_breakout",
    "mean_reversion",
    "trend_pullback",
    "volatility_expansion",
}

ALLOWED_FILTERS: Set[str] = {
    "liquidity",
    "volatility",
    "spread",
    "session",
}

ALLOWED_RISK_MODELS: Set[str] = {
    "fixed_stop",
    "atr_stop",
    "time_stop",
}

ALLOWED_EXIT_MODELS: Set[str] = {
    "time_decay",
    "signal_reversal",
}

ALLOWED_SIZING_MODELS: Set[str] = {
    "fixed_fraction",
    "confidence_weighted",
}


# ======================================================
# Alpha Genome Validator
# ======================================================

class AlphaGenomeValidator:
    """
    Deterministic, explainable genome rejection engine.

    This is NOT fitness.
    This is NOT scoring.
    This is elimination.
    """

    @staticmethod
    def validate(genome: AlphaGenome) -> None:
        errors: List[str] = []

        # ---- Signal ----
        if genome.signal_type not in ALLOWED_SIGNALS:
            errors.append(f"Unknown signal_type: {genome.signal_type}")

        # ---- Filters ----
        unknown_filters = set(genome.filters) - ALLOWED_FILTERS
        if unknown_filters:
            errors.append(f"Unknown filters: {sorted(unknown_filters)}")

        # ---- Risk ----
        if genome.risk_model not in ALLOWED_RISK_MODELS:
            errors.append(f"Unknown risk_model: {genome.risk_model}")

        # ---- Exit ----
        if genome.exit_model not in ALLOWED_EXIT_MODELS:
            errors.append(f"Unknown exit_model: {genome.exit_model}")

        # ---- Sizing ----
        if genome.sizing_model not in ALLOWED_SIZING_MODELS:
            errors.append(f"Unknown sizing_model: {genome.sizing_model}")

        # ---- Regime Gating ----
        if not genome.allowed_regimes:
            errors.append("allowed_regimes cannot be empty")

        # ---- Fail Fast ----
        if errors:
            raise StrategyValidationError("; ".join(errors))
