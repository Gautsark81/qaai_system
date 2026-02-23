from __future__ import annotations
from typing import Dict, Iterable, List, Any
import pandas as pd

from modules.strategy.base import Strategy, Signal
from modules.strategy.strategy_factory import StrategyFactory as RuleEngineFactory


class StreamRuleAdapter(Strategy):
    """
    Lightweight streaming adapter for real-time rule evaluation.

    - Designed for single-row, streaming inputs (e.g., websocket ticks)
    - Uses StrategyFactory (rule engine) internally
    - Maintains optional small rolling history if needed
    - Completely non-invasive to existing strategy system
    """

    def __init__(self, strategy_id: str, config: Dict[str, Any]):
        self.strategy_id = strategy_id

        # rule engine config must be under "rules_cfg" or given as top-level config
        self.rule_cfg = config.get("rules_cfg", config)

        # create the rule-engine instance
        self.engine = RuleEngineFactory(self.rule_cfg)

        # internal rolling buffer (optional)
        self._history: List[Dict[str, Any]] = []
        self.max_history = int(self.rule_cfg.get("max_history", 0))  # default = no history

    # ------------------------------------------------------------------
    # Strategy Protocol: prepare(historical_features)
    # ------------------------------------------------------------------
    def prepare(self, historical_features: Iterable[Dict[str, Any]]) -> None:
        """
        For streaming strategies, prepare just initializes rolling history.
        """
        if self.max_history > 0:
            self._history = list(historical_features)[-self.max_history :]
        else:
            self._history = []
        return None

    # ------------------------------------------------------------------
    # Strategy Protocol: generate_signals(latest_features) -> List[Signal]
    # ------------------------------------------------------------------
    def generate_signals(self, latest_features: Dict[str, Any]) -> List[Signal]:
        """
        Accepts a single-row dict representing the latest market features.
        Produces a list of Signal objects based on rule evaluation.
        """
        # update rolling history
        if self.max_history > 0:
            self._history.append(dict(latest_features))
            if len(self._history) > self.max_history:
                self._history.pop(0)

        # Convert to one-row DataFrame
        df = pd.DataFrame([latest_features])
        out = self.engine.generate_signals(df)

        # signal = -1, 0, 1
        s_val = int(out.loc[0, "signal"]) if "signal" in out.columns else 0
        if s_val == 0:
            return []

        # Map signal value to BUY / SELL
        side = "BUY" if s_val > 0 else "SELL"

        # optional configurable size
        size = float(self.rule_cfg.get("default_size", 1.0))

        sig = Signal(
            strategy_id=self.strategy_id,
            symbol=str(latest_features.get("symbol", "UNKNOWN")),
            side=side,
            size=size,
            score=float(s_val),
            meta={"rule_row": latest_features}
        )
        return [sig]
