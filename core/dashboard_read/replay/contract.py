from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence, Optional

from core.dashboard_read.snapshot import SystemSnapshot
from core.dashboard_read.replay.result import ReplayResult
from core.dashboard_read.replay.failures import ReplayFailure


@dataclass(frozen=True)
class ReplayContract:
    """
    Immutable declaration of offline replay guarantees.

    This object is *not* an engine.
    It is a contract auditors can read and reason about.
    """

    requires_sealed_snapshot: bool = True
    providers_allowed: bool = False
    side_effects_allowed: bool = False
    wall_clock_allowed: bool = False
    randomness_allowed: bool = False
    network_allowed: bool = False


class ReplayEngine(ABC):
    """
    Strict interface for offline replay engines.

    Implementations MUST:
    - accept exactly one input: SystemSnapshot
    - produce a ReplayResult
    - never raise for expected failures
    - classify all failures explicitly
    """

    contract: ReplayContract = ReplayContract()

    @abstractmethod
    def replay(self, snapshot: SystemSnapshot) -> ReplayResult:
        """
        Perform an offline deterministic replay of a sealed snapshot.

        Implementations MUST:
        - verify snapshot integrity first
        - never mutate snapshot
        - never touch providers
        - never depend on wall-clock, randomness, or IO
        """
        raise NotImplementedError