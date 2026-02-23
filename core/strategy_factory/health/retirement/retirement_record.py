from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

@dataclass(frozen=True)
class RetirementRecord:
    strategy_id: str
    from_state: str
    to_state: str
    reason_code: str
    trigger_source: str
    metrics_snapshot: Dict[str, Any]
    actor: str
    timestamp: datetime
