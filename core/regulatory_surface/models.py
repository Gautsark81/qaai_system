from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class RegulatoryExport:
    """
    Deterministic export artifact intended for regulators.
    """

    export_type: str
    generated_at: int
    payload: Dict[str, str]


@dataclass(frozen=True)
class AuditBundle:
    """
    Time-boxed audit bundle.

    Contains immutable references to evidence and explanations
    within a bounded time window.
    """

    start_timestamp: int
    end_timestamp: int
    artifacts: List[RegulatoryExport]


@dataclass(frozen=True)
class ExplainabilityPacket:
    """
    Human- and regulator-readable explanation packet.
    """

    timestamp: int
    summary: Dict[str, str]
