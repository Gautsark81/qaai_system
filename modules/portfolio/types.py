from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class PortfolioIntent:
    """
    Portfolio-level intent derived from one or more StrategyIntents,
    after allocation and caps are applied.

    This is the LAST abstraction before execution planning.
    Execution must treat this as read-only.
    """

    strategy_id: str
    symbol: str
    side: str  # "BUY" | "SELL"
    quantity: int
    price: Optional[float] = None

    # Audit / traceability
    allocation_fraction: float = 0.0
    allocation_notional: float = 0.0

    # Deterministic metadata (never used for logic)
    metadata: Dict[str, object] = field(default_factory=dict)

    def is_executable(self) -> bool:
        """
        Portfolio-level guard.
        Execution must not second-guess this.
        """
        return self.quantity > 0


@dataclass(frozen=True)
class PortfolioPlan:
    """
    Immutable plan produced by PortfolioManager.

    Properties:
    - Deterministic
    - Restart-safe
    - Serializable
    - No side effects
    """

    intents: List[PortfolioIntent]
    total_notional: float

    # Diagnostic-only (never logic-driving)
    diagnostics: Dict[str, object] = field(default_factory=dict)

    def executable_intents(self) -> List[PortfolioIntent]:
        """
        Filtered view used by ExecutionGate.
        """
        return [i for i in self.intents if i.is_executable()]

    def is_empty(self) -> bool:
        return len(self.executable_intents()) == 0
