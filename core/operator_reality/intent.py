from typing import Optional
from .models import OperatorIntent


class OperatorIntentFactory:
    """
    Factory for creating deterministic operator intent objects.

    This factory:
    - does NOT read system time
    - does NOT persist data
    - does NOT touch execution
    - does NOT validate strategy or capital

    It only packages a human decision into an immutable record.
    """

    @staticmethod
    def create(
        *,
        operator_id: str,
        intent_type: str,
        scope: str,
        timestamp: int,
        note: Optional[str] = None,
    ) -> OperatorIntent:
        if not operator_id:
            raise ValueError("operator_id must be provided")

        if not intent_type:
            raise ValueError("intent_type must be provided")

        if not scope:
            raise ValueError("scope must be provided")

        if not isinstance(timestamp, int):
            raise ValueError("timestamp must be an integer")

        return OperatorIntent(
            operator_id=operator_id,
            intent_type=intent_type,
            scope=scope,
            timestamp=timestamp,
            note=note,
        )
