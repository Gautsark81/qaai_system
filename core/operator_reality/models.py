from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OperatorIntent:
    """
    Immutable declaration of operator intent.

    This represents a *human decision*, not an action.
    It does not trigger execution, strategy changes, or capital movement.

    Examples of intent_type:
    - ENABLE_LIVE
    - RECONFIRM_LIVE
    - RECOVER_AFTER_CRASH
    - ACKNOWLEDGE_INCIDENT
    """

    operator_id: str
    intent_type: str
    scope: str
    timestamp: int
    note: Optional[str] = None


@dataclass(frozen=True)
class OperatorAcknowledgment:
    """
    Immutable acknowledgment record.

    This object is used for:
    - audit
    - replay
    - regulatory explanation
    - downstream governance checks

    It is *never* used to directly control execution.
    """

    intent: OperatorIntent
    acknowledged: bool
    evidence_id: str
