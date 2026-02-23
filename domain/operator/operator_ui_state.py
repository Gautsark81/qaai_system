from dataclasses import dataclass
from typing import List
from domain.observability.system_health import SystemHealthSnapshot
from domain.observability.alert import Alert


@dataclass(frozen=True)
class OperatorUIState:
    system_health: SystemHealthSnapshot
    active_alerts: List[Alert]
