# modules/strategy_tournament/gate_decision.py

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class GateDecision:
    strategy_id: str
    passed: bool
    failed_reasons: List[str]

    @property
    def is_pass(self) -> bool:
        return self.passed
