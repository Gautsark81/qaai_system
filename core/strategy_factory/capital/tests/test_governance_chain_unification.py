# core/strategy_factory/capital/tests/test_governance_chain_unification.py

from datetime import datetime, timezone

from core.strategy_factory.capital.governance_chain import (
    generate_governance_chain_id,
    reconstruct_governance_episode,
)


def test_governance_chain_id_is_deterministic():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    id1 = generate_governance_chain_id(
        strategy_dna="alpha",
        episode_started_at=now,
        episode_type="CAPITAL_EPISODE",
        deterministic_payload="event1|event2",
    )

    id2 = generate_governance_chain_id(
        strategy_dna="alpha",
        episode_started_at=now,
        episode_type="CAPITAL_EPISODE",
        deterministic_payload="event1|event2",
    )

    assert id1 == id2


def test_governance_chain_id_changes_on_payload_change():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    id1 = generate_governance_chain_id(
        strategy_dna="alpha",
        episode_started_at=now,
        episode_type="CAPITAL_EPISODE",
        deterministic_payload="event1|event2",
    )

    id2 = generate_governance_chain_id(
        strategy_dna="alpha",
        episode_started_at=now,
        episode_type="CAPITAL_EPISODE",
        deterministic_payload="event1|event3",
    )

    assert id1 != id2


def test_reconstruction_is_deterministic():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    episode1 = reconstruct_governance_episode(
        strategy_dna="alpha",
        episode_started_at=now,
        episode_type="CAPITAL_EPISODE",
        event_payloads=["A", "B", "C"],
    )

    episode2 = reconstruct_governance_episode(
        strategy_dna="alpha",
        episode_started_at=now,
        episode_type="CAPITAL_EPISODE",
        event_payloads=["A", "B", "C"],
    )

    assert episode1.governance_chain_id == episode2.governance_chain_id
    assert episode1.fingerprint() == episode2.fingerprint()


def test_reconstruction_detects_mutation():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    episode1 = reconstruct_governance_episode(
        strategy_dna="alpha",
        episode_started_at=now,
        episode_type="CAPITAL_EPISODE",
        event_payloads=["A", "B", "C"],
    )

    episode2 = reconstruct_governance_episode(
        strategy_dna="alpha",
        episode_started_at=now,
        episode_type="CAPITAL_EPISODE",
        event_payloads=["A", "B", "X"],
    )

    assert episode1.governance_chain_id != episode2.governance_chain_id