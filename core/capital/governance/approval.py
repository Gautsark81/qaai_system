from datetime import datetime
from typing import Optional
from core.capital.governance.decision import CapitalGovernanceDecision


class CapitalGovernanceGate:
    """
    Final authority before capital is deployed.

    No execution.
    No capital mutation.
    Only governance decisions.
    """

    def evaluate(
        self,
        *,
        strategy_dna: str,
        stress_breach: bool,
        concentration_breach: bool,
        operator: Optional[str] = None,
    ) -> CapitalGovernanceDecision:

        if stress_breach or concentration_breach:
            return CapitalGovernanceDecision(
                strategy_dna=strategy_dna,
                decision="BLOCK",
                reason="CAPITAL_RISK_BREACH",
                approved_by=None,
                timestamp=datetime.utcnow(),
            )

        if operator:
            return CapitalGovernanceDecision(
                strategy_dna=strategy_dna,
                decision="APPROVE",
                reason="OPERATOR_APPROVAL",
                approved_by=operator,
                timestamp=datetime.utcnow(),
            )

        return CapitalGovernanceDecision(
            strategy_dna=strategy_dna,
            decision="ESCALATE",
            reason="AWAITING_OPERATOR_APPROVAL",
            approved_by=None,
            timestamp=datetime.utcnow(),
        )
