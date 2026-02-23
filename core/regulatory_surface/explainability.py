from typing import Dict
from .models import ExplainabilityPacket


class ExplainabilityBuilder:
    """
    Builds regulator-readable explanation packets.

    Uses summaries already produced by governance and operator layers.
    """

    @staticmethod
    def build(
        *,
        timestamp: int,
        summary: Dict[str, str],
    ) -> ExplainabilityPacket:
        if not isinstance(timestamp, int):
            raise ValueError("timestamp must be deterministic integer")

        if not isinstance(summary, dict):
            raise ValueError("summary must be a dict")

        return ExplainabilityPacket(
            timestamp=timestamp,
            summary=dict(summary),
        )
