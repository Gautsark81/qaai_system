from dataclasses import dataclass
from typing import Set, Dict

from core.regime.taxonomy import MarketRegime


@dataclass(frozen=True)
class AlphaActivationRule:
    """
    Defines where a strategy is allowed to operate.

    Immutable by design.
    """
    strategy_name: str
    allowed_regimes: Set[MarketRegime]


class AlphaActivationMatrix:
    """
    Canonical alpha ↔ regime activation controller.

    Pure logic:
    - no side effects
    - no execution imports
    """

    def __init__(self, rules: Dict[str, AlphaActivationRule]):
        self._rules = rules

    def is_active(
        self,
        *,
        strategy_name: str,
        regime: MarketRegime,
    ) -> bool:
        """
        Returns True if the strategy is allowed to operate
        in the given regime.
        """
        rule = self._rules.get(strategy_name)

        # Default: conservative OFF if not explicitly mapped
        if rule is None:
            return False

        return regime in rule.allowed_regimes
