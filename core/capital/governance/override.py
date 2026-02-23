from datetime import datetime
from core.capital.governance.decision import CapitalGovernanceDecision


class CapitalOverrideProtocol:
    """
    Explicit, logged human override.
    """

    def override(
        self,
        *,
        strategy_dna: str,
        operator: str,
        reason: str,
    ) -> CapitalGovernanceDecision:

        return CapitalGovernanceDecision(
            strategy_dna=strategy_dna,
            decision="APPROVE",
            reason=f"OVERRIDE:{reason}",
            approved_by=operator,
            timestamp=datetime.utcnow(),
        )
