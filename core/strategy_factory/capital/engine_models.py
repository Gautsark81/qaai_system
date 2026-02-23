from dataclasses import dataclass
from typing import Optional

from core.strategy_factory.capital.governance_models import (
    CapitalGovernanceDecision,
)
from core.strategy_factory.capital.throttling_models import (
    CapitalThrottleDecision,
)


@dataclass(frozen=True)
class CapitalEngineResult:
    """
    Full deterministic output of capital engine (C4+).

    Order of evaluation:
    1. governance
    2. throttle
    3. allocation
    """

    governance: CapitalGovernanceDecision
    governance_audit: object
    throttle: Optional[CapitalThrottleDecision]
    allocation: Optional[object]
