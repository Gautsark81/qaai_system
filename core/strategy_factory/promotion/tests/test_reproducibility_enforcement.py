import pytest
from pathlib import Path

from core.strategy_factory.promotion.engine import AutonomousPromotionEngine
from core.reproducibility.vault_store import VaultStore
from core.reproducibility.vault_service import VaultService
from core.strategy_factory.health.evaluator import PromotionEvidence
from core.strategy_factory.capital.evaluator import CapitalFeasibilityEvidence
from core.strategy_factory.capital.attribution import CapitalConstraintEvidence
from core.strategy_factory.capital.sizing import CapitalSizingEvidence


DNA = "DNA1"


# ---------------------------------------------------------------------
# Test Utilities (EXACTLY match real constructors)
# ---------------------------------------------------------------------

def build_minimal_feasibility():
    return CapitalFeasibilityEvidence(
        strategy_dna=DNA,
        feasible=True,
        reasons=[]
    )


def build_minimal_constraint():
    return CapitalConstraintEvidence(
        strategy_dna=DNA,
        binding_constraint="none",
        slack=0.0,
        explanation="No binding capital constraints",
    )


def build_minimal_sizing():
    return CapitalSizingEvidence(
        strategy_dna=DNA,
        recommended_fraction=0.1,
        binding_constraint="none",
        explanation="Capital sized within limits",
    )


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_block_without_reproducibility_record(tmp_path: Path):

    vault = VaultStore(tmp_path / "vault.jsonl")
    engine = AutonomousPromotionEngine(vault_store=vault)

    promotion = PromotionEvidence(
        strategy_dna=DNA,
        promotable=True,
        reasons=[],
        last_evaluated_at=None,
        reproducibility_record_id=None,
    )

    decision = engine.decide(
        promotion=promotion,
        feasibility=build_minimal_feasibility(),
        constraint=build_minimal_constraint(),
        sizing=build_minimal_sizing(),
    )

    assert decision.promote is False
    assert "Missing reproducibility vault record" in decision.reasons


def test_block_if_record_missing_in_vault(tmp_path: Path):

    vault = VaultStore(tmp_path / "vault.jsonl")
    engine = AutonomousPromotionEngine(vault_store=vault)

    promotion = PromotionEvidence(
        strategy_dna=DNA,
        promotable=True,
        reasons=[],
        last_evaluated_at=None,
        reproducibility_record_id="fake-id",
    )

    decision = engine.decide(
        promotion=promotion,
        feasibility=build_minimal_feasibility(),
        constraint=build_minimal_constraint(),
        sizing=build_minimal_sizing(),
    )

    assert decision.promote is False
    assert "Reproducibility vault record not found" in decision.reasons


def test_allow_promotion_with_valid_record(tmp_path: Path):

    vault = VaultStore(tmp_path / "vault.jsonl")
    service = VaultService(vault)
    engine = AutonomousPromotionEngine(vault_store=vault)

    record_id = service.register_record(
        hypothesis_id="H1",
        hypothesis_hash="hh",
        data_hash="dd",
        feature_hash="ff",
        parameter_hash="pp",
        code_hash="cc",
        env_hash="ee",
        ssr_hash="ss",
    )

    promotion = PromotionEvidence(
        strategy_dna=DNA,
        promotable=True,
        reasons=[],
        last_evaluated_at=None,
        reproducibility_record_id=record_id,
    )

    decision = engine.decide(
        promotion=promotion,
        feasibility=build_minimal_feasibility(),
        constraint=build_minimal_constraint(),
        sizing=build_minimal_sizing(),
    )

    assert decision.promote is True
    assert decision.recommended_fraction > 0