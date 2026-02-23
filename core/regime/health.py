from collections import defaultdict
from typing import Dict, List, Any, Union

from core.regime.taxonomy import MarketRegime


class StrategyHealth:
    """
    Stateful tracker for strategy performance across market regimes.
    Computes Strategy Success Ratio (SSR).
    """

    def __init__(self):
        self._records: Dict[MarketRegime, List[bool]] = defaultdict(list)

    # --------------------------------------------------
    # Public API (required by regime tests)
    # --------------------------------------------------

    def record_outcome(self, *, regime: MarketRegime, success: bool) -> None:
        self._records[regime].append(bool(success))

    def ssr_for(self, regime: MarketRegime) -> float:
        records = self._records.get(regime, [])
        if not records:
            return 0.0
        return sum(records) / len(records)

    def overall_ssr(self) -> float:
        all_records = [
            outcome
            for records in self._records.values()
            for outcome in records
        ]
        if not all_records:
            return 0.0
        return sum(all_records) / len(all_records)


# ======================================================
# Read-only snapshot adapter (USED BY EXPLAINABILITY)
# ======================================================

def strategy_health_snapshot(
    source: Union[StrategyHealth, Any],
) -> Dict[str, Any]:
    """
    Produce an immutable, serializable snapshot of strategy health.

    Accepts either:
    - StrategyHealth
    - StrategyRecord (with optional .health or .strategy_health)

    This function MUST NOT mutate input.
    """

    # -----------------------------------------------
    # Resolve StrategyHealth safely
    # -----------------------------------------------

    if isinstance(source, StrategyHealth):
        health = source
    else:
        # StrategyRecord path (dashboard / explainability)
        health = getattr(source, "health", None) or getattr(
            source, "strategy_health", None
        )

    # -----------------------------------------------
    # No health data yet → safe zero snapshot
    # -----------------------------------------------

    if not isinstance(health, StrategyHealth):
        return {
            "overall_ssr": 0.0,
            "by_regime": {
                regime.value: {"ssr": 0.0, "observations": 0}
                for regime in MarketRegime
            },
        }

    # -----------------------------------------------
    # Normal snapshot
    # -----------------------------------------------

    return {
        "overall_ssr": health.overall_ssr(),
        "by_regime": {
            regime.value: {
                "ssr": health.ssr_for(regime),
                "observations": len(health._records.get(regime, [])),
            }
            for regime in MarketRegime
        },
    }
