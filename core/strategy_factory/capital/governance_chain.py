# core/strategy_factory/capital/governance_chain.py

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List


# ==========================================================
# Governance Chain Identity
# ==========================================================


def _hash(payload: str) -> str:
    return hashlib.sha256(payload.encode()).hexdigest()


def generate_governance_chain_id(
    *,
    strategy_dna: str,
    episode_started_at: datetime,
    episode_type: str,
    deterministic_payload: str,
) -> str:
    """
    Deterministic governance chain ID.

    MUST be:
    - Replay safe
    - Deterministic
    - Not dependent on wall clock
    - Pure function

    Inputs must be fully deterministic.
    """

    base = (
        f"{strategy_dna}|"
        f"{episode_started_at.isoformat()}|"
        f"{episode_type}|"
        f"{deterministic_payload}"
    )

    return _hash(base)


# ==========================================================
# Governance Episode Model
# ==========================================================


@dataclass(frozen=True)
class GovernanceEpisode:
    """
    Immutable representation of a governance episode.
    """

    governance_chain_id: str
    strategy_dna: str
    episode_type: str
    started_at: datetime
    events: List[str]

    def fingerprint(self) -> str:
        """
        Deterministic fingerprint of entire episode.
        """

        payload = (
            f"{self.governance_chain_id}|"
            f"{self.strategy_dna}|"
            f"{self.episode_type}|"
            f"{self.started_at.isoformat()}|"
            f"{'|'.join(self.events)}"
        )

        return _hash(payload)


# ==========================================================
# Reconstruction Engine
# ==========================================================


def reconstruct_governance_episode(
    *,
    strategy_dna: str,
    episode_started_at: datetime,
    episode_type: str,
    event_payloads: Iterable[str],
) -> GovernanceEpisode:
    """
    Deterministically reconstruct a governance episode.
    """

    events = list(event_payloads)

    deterministic_payload = "|".join(events)

    chain_id = generate_governance_chain_id(
        strategy_dna=strategy_dna,
        episode_started_at=episode_started_at,
        episode_type=episode_type,
        deterministic_payload=deterministic_payload,
    )

    return GovernanceEpisode(
        governance_chain_id=chain_id,
        strategy_dna=strategy_dna,
        episode_type=episode_type,
        started_at=episode_started_at,
        events=events,
    )