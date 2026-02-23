from dataclasses import dataclass
from typing import Callable

from .events import ObservabilityEvent


@dataclass
class AlertRule:
    """
    Pure alert predicate.
    """
    name: str
    condition: Callable[[ObservabilityEvent], bool]


class AlertEngine:
    """
    Stateless alert evaluator.
    """

    def __init__(self, rules):
        self.rules = rules

    def evaluate(self, event):
        return [
            rule.name
            for rule in self.rules
            if rule.condition(event)
        ]
