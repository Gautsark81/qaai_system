from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional


DrillType = Literal[
    "kill_switch",
    "latency_spike",
    "slippage_breach",
    "data_feed_loss",
    "operator_override",
]


@dataclass(frozen=True)
class OpsDrill:
    drill_id: str
    drill_type: DrillType
    target: str            # strategy_id or "system"
    initiated_by: str
    initiated_at: datetime
    expected_response: str
    notes: Optional[str] = None
