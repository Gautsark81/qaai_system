from typing import Dict, Optional

from .snapshot import OperatorSnapshot
from .models import OperatorIntent


class OperatorSnapshotBuilder:
    """
    Deterministic operator snapshot constructor.

    This builder:
    - reads governance and telemetry inputs
    - performs no validation
    - performs no execution
    - performs no mutation
    """

    @staticmethod
    def build(
        *,
        timestamp: int,
        mode: str,
        strategy_id: Optional[str],
        last_intent: OperatorIntent,
        governance_checks: Dict[str, str],
        capital_view: Dict[str, str],
        notes: Optional[str] = None,
    ) -> OperatorSnapshot:
        if not isinstance(timestamp, int):
            raise ValueError("timestamp must be deterministic integer")

        if not mode:
            raise ValueError("mode must be provided")

        if not isinstance(governance_checks, dict):
            raise ValueError("governance_checks must be a dict")

        if not isinstance(capital_view, dict):
            raise ValueError("capital_view must be a dict")

        return OperatorSnapshot(
            timestamp=timestamp,
            mode=mode,
            strategy_id=strategy_id,
            last_operator_intent=last_intent.intent_type,
            governance_summary=dict(governance_checks),
            capital_summary=dict(capital_view),
            notes=notes,
        )
