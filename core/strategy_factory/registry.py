from dataclasses import dataclass, field
from typing import Dict, Optional, List, ClassVar
from datetime import datetime

from core.strategy_factory.dna import compute_strategy_dna
from core.strategy_factory.spec import StrategySpec
from core.strategy_factory.exceptions import (
    DuplicateStrategyError,
    ExecutionNotAllowed,
)


# ======================================================
# Strategy Record (PURE DATA OBJECT)
# ======================================================

@dataclass
class StrategyRecord:
    """
    Immutable identity + mutable lifecycle container.

    IMPORTANT:
    - Registry mutates records
    - UI / dashboards MUST NOT
    """

    dna: str
    spec: StrategySpec

    # Lifecycle (PUBLIC / LEGACY VISIBLE)
    state: str = "GENERATED"

    # Intelligence / Analytics
    ssr: Optional[float] = None
    health: Dict = field(default_factory=dict)

    # Audit trail (append-only)
    history: List[dict] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_updated(self, *, reason: str) -> None:
        self.updated_at = datetime.utcnow()
        self.history.append(
            {
                "timestamp": self.updated_at,
                "event": reason,
            }
        )


# ======================================================
# Strategy Registry (SINGLE SOURCE OF TRUTH)
# ======================================================

class StrategyRegistry:
    """
    Canonical registry for all strategies.

    Guarantees:
    - Deterministic identity (DNA)
    - No duplicates
    - Lifecycle state ownership
    - Execution gating
    - Dashboard-safe global access (read-only)
    """

    EXECUTABLE_STATES = {"PAPER", "LIVE"}

    _GLOBAL: ClassVar[Optional["StrategyRegistry"]] = None

    def __init__(self):
        self._records: Dict[str, StrategyRecord] = {}

        # Lifecycle event store (Phase-9+)
        self._lifecycle_history: Dict[str, List[dict]] = {}

        # Resurrection / special events
        self._events: Dict[str, List[dict]] = {}

        if StrategyRegistry._GLOBAL is None:
            StrategyRegistry._GLOBAL = self

    # --------------------------------------------------
    # Core API
    # --------------------------------------------------

    def register(self, spec: StrategySpec) -> StrategyRecord:
        dna = compute_strategy_dna(spec)

        if dna in self._records:
            raise DuplicateStrategyError(f"Duplicate strategy: {dna}")

        record = StrategyRecord(
            dna=dna,
            spec=spec,
            state="GENERATED",
        )
        record.mark_updated(reason="REGISTERED")

        self._records[dna] = record
        self._lifecycle_history[dna] = []

        return record

    def get(self, dna: str) -> StrategyRecord:
        return self._records[dna]

    def all(self) -> Dict[str, StrategyRecord]:
        return dict(self._records)

    # --------------------------------------------------
    # Phase-11: Resurrection Lifecycle Hook (ADDITIVE)
    # --------------------------------------------------

    def mark_resurrection_candidate(
        self,
        dna: str,
        *,
        state: str,
        reason: str,
        artifact: object,
    ) -> None:
        """
        Mark a strategy as entering resurrection evaluation.

        RULES:
        - Registry owns the state mutation
        - Execution is NOT allowed in this state
        - Artifact is stored for audit / dashboards
        """

        record = self._records.get(dna)
        if record is None:
            raise KeyError(f"Unknown strategy DNA: {dna}")

        previous_state = record.state
        record.state = state
        record.mark_updated(
            reason=f"{previous_state} → {state} (RESURRECTION)"
        )

        self._events.setdefault(dna, []).append(
            {
                "timestamp": datetime.utcnow(),
                "type": "RESURRECTION_CANDIDATE",
                "from": previous_state,
                "to": state,
                "reason": reason,
                "artifact": artifact,
            }
        )

    # --------------------------------------------------
    # Lifecycle Integration (Phase-9)
    # --------------------------------------------------

    def apply_lifecycle_event(self, event) -> None:
        record = self._records[event.strategy_dna]

        record.state = event.to_state.value
        record.mark_updated(
            reason=f"{event.from_state.value} → {event.to_state.value} ({event.trigger})"
        )

        self._lifecycle_history[event.strategy_dna].append(
            {
                "timestamp": event.timestamp,
                "from": event.from_state.value,
                "to": event.to_state.value,
                "trigger": event.trigger,
                "reason": event.reason,
            }
        )

    def lifecycle_history(self, dna: str) -> List[dict]:
        return list(self._lifecycle_history.get(dna, []))

    # --------------------------------------------------
    # Execution Governance
    # --------------------------------------------------

    def assert_can_execute(self, dna: str) -> None:
        record = self._records.get(dna)

        if record is None:
            raise ExecutionNotAllowed(f"Unknown strategy: {dna}")

        if record.state not in self.EXECUTABLE_STATES:
            raise ExecutionNotAllowed(
                f"Strategy {dna} not executable (state={record.state})"
            )

    # --------------------------------------------------
    # Dashboard / Audit
    # --------------------------------------------------

    def record_resurrection_event(self, dna: str, event: str) -> None:
        self._events.setdefault(dna, []).append(
            {
                "event": event,
                "timestamp": datetime.utcnow(),
            }
        )

    def get_events(self, dna: str) -> List[dict]:
        return self._events.get(dna, [])

    # --------------------------------------------------
    # Global Access
    # --------------------------------------------------

    @classmethod
    def global_instance(cls) -> "StrategyRegistry":
        if cls._GLOBAL is None:
            cls._GLOBAL = cls()
        return cls._GLOBAL
