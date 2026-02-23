from typing import List, Dict

from core.capital.usage_ledger.ledger import CapitalUsageLedger
from core.capital.coordination.models import (
    CapitalRequest,
    CoordinationDecision,
)


class CapitalCoordinator:
    """
    Phase 24.2 — Multi-Strategy Capital Coordination

    Responsibilities:
    - Respect global capital ceiling
    - Respect already-engaged capital (ledger)
    - Deterministically resolve conflicts
    - Produce explainable decisions
    """

    def __init__(self, total_capital: float):
        self._total_capital = total_capital

    def coordinate(
        self,
        requests: List[CapitalRequest],
        ledger: CapitalUsageLedger,
    ) -> CoordinationDecision:

        engaged = ledger.total_used_capital()
        available = max(self._total_capital - engaged, 0.0)

        granted: Dict[str, float] = {}
        explanations: Dict[str, str] = {}

        # Deterministic order: strategy_id
        for req in sorted(requests, key=lambda r: r.strategy_id):
            if available <= 0:
                granted_amt = 0.0
            else:
                granted_amt = min(req.requested_amount, available)

            granted[req.strategy_id] = granted_amt
            explanations[req.strategy_id] = (
                f"requested={req.requested_amount}, "
                f"granted={granted_amt}, "
                f"available_before={available}"
            )

            available -= granted_amt

        return CoordinationDecision(
            granted=granted,
            remaining_capital=available,
            explanations=explanations,
        )
