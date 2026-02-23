import pytest

from core.strategy_factory.dna import AlphaGenome
from core.strategy_factory.validators import AlphaGenomeValidator
from core.strategy_factory.exceptions import StrategyValidationError


def test_valid_genome_passes():
    genome = AlphaGenome(
        allowed_regimes=["TRENDING_UP"],
        signal_type="momentum_breakout",
        filters=["liquidity"],
        risk_model="atr_stop",
        exit_model="time_decay",
        sizing_model="fixed_fraction",
    )

    AlphaGenomeValidator.validate(genome)


def test_unknown_signal_rejected():
    genome = AlphaGenome(
        allowed_regimes=["TRENDING_UP"],
        signal_type="magic_signal",
    )

    with pytest.raises(StrategyValidationError):
        AlphaGenomeValidator.validate(genome)


def test_unknown_filter_rejected():
    genome = AlphaGenome(
        allowed_regimes=["RANGE"],
        signal_type="mean_reversion",
        filters=["liquidity", "astrology"],
    )

    with pytest.raises(StrategyValidationError):
        AlphaGenomeValidator.validate(genome)


def test_empty_regime_list_rejected():
    genome = AlphaGenome(
        allowed_regimes=[],
        signal_type="momentum_breakout",
    )

    with pytest.raises(StrategyValidationError):
        AlphaGenomeValidator.validate(genome)
