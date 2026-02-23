from core.execution.broker_response.models import BrokerResponse
from core.execution.broker_response.governance.outcome import BrokerOutcome
from core.execution.broker_response.governance.rules import classify_response


class ResponseClassifier:
    """
    Pure, deterministic response classifier.

    Guarantees:
    - NO execution authority
    - NO retries
    - NO mutation
    - Governance-level semantic correctness
    """

    @staticmethod
    def classify(response: BrokerResponse) -> BrokerOutcome:
        """
        Classify broker response into a governance outcome.

        Governance invariant:
        - Zero filled quantity is ALWAYS a REJECTED outcome
        - Never escalated to TERMINAL_FAILURE
        """

        # --------------------------------------------------
        # GOVERNANCE INVARIANT (CRITICAL FIX)
        # --------------------------------------------------
        if response.filled_quantity == 0:
            return BrokerOutcome.REJECTED

        # --------------------------------------------------
        # FALL BACK TO CANONICAL RULE MATRIX
        # --------------------------------------------------
        return classify_response(response)


__all__ = ["ResponseClassifier"]
