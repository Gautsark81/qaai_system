from core.strategy_factory.promotion.promotion_intelligence_trace import (
    build_promotion_intelligence_trace,
    compute_promotion_trace_hash,
)


def test_trace_hash_deterministic():
    h1 = compute_promotion_trace_hash(
        strategy_dna="DNA1",
        intelligence_hash="ihash",
        screening_hash="shash",
        capital_governance_chain_id="chain1",
        lifecycle_state="PAPER",
    )

    h2 = compute_promotion_trace_hash(
        strategy_dna="DNA1",
        intelligence_hash="ihash",
        screening_hash="shash",
        capital_governance_chain_id="chain1",
        lifecycle_state="PAPER",
    )

    assert h1 == h2


def test_trace_changes_when_any_component_changes():
    base = compute_promotion_trace_hash(
        strategy_dna="DNA1",
        intelligence_hash="ihash",
        screening_hash="shash",
        capital_governance_chain_id="chain1",
        lifecycle_state="PAPER",
    )

    altered = compute_promotion_trace_hash(
        strategy_dna="DNA1",
        intelligence_hash="DIFFERENT",
        screening_hash="shash",
        capital_governance_chain_id="chain1",
        lifecycle_state="PAPER",
    )

    assert base != altered


def test_trace_builder_contract():
    trace = build_promotion_intelligence_trace(
        strategy_dna="DNA1",
        intelligence_hash="ihash",
        screening_hash="shash",
        capital_governance_chain_id="chain1",
        lifecycle_state="PAPER",
    )

    assert trace.strategy_dna == "DNA1"
    assert trace.intelligence_hash == "ihash"
    assert trace.screening_hash == "shash"
    assert trace.capital_governance_chain_id == "chain1"
    assert trace.lifecycle_state == "PAPER"
    assert trace.composite_trace_hash is not None