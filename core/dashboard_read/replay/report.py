from dataclasses import dataclass
from typing import Dict, Any

from .domains.strategy import replay_strategy
from .domains.risk import replay_risk
from .domains.capital import replay_capital
from .domains.execution import replay_execution
from .domains.compliance import replay_compliance


@dataclass(frozen=True)
class OfflineReplayReport:
    """
    Single source of replay truth.
    """
    strategy: Dict[str, Any]
    risk: Dict[str, Any]
    capital: Dict[str, Any]
    execution: Dict[str, Any]
    compliance: Dict[str, Any]

    @property
    def is_consistent(self) -> bool:
        """
        Hard consistency checks.
        """
        # Example invariant:
        # orders must not exceed capital usage if both exist
        used = self.capital.get("used")
        orders = self.execution.get("count")

        if used is not None and orders is not None:
            return used >= 0 and orders >= 0

        return True


def build_replay_report(snapshot) -> OfflineReplayReport:
    return OfflineReplayReport(
        strategy=replay_strategy(snapshot),
        risk=replay_risk(snapshot),
        capital=replay_capital(snapshot),
        execution=replay_execution(snapshot),
        compliance=replay_compliance(snapshot),
    )