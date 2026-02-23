# modules/strategy/rule_adapter.py
from __future__ import annotations
from typing import Dict, Iterable, List, Any
import pandas as pd

from modules.strategy.base import Strategy, Signal
from modules.strategy.strategy_factory import StrategyFactory as RuleEngineFactory

class RuleEngineAdapter(Strategy):
    """
    Adapter that implements the Strategy Protocol but uses the rule-based
    StrategyFactory (rule engine) under the hood.

    - config: dict expected by rule engine (rules/signals). Pass-through.
    - strategy_id: identifier for Strategy Protocol.
    """

    def __init__(self, strategy_id: str, config: Dict[str, Any]):
        self.strategy_id = strategy_id
        # Keep a copy of rule config for the engine
        self.rule_cfg = config.get("rules_cfg", config)
        # create the engine
        self.engine = RuleEngineFactory(self.rule_cfg)
        # small ring-buffer of historical features as list[dict]
        self._history: List[Dict[str, Any]] = []

    def prepare(self, historical_features: Iterable[Dict[str, Any]]) -> None:
        # store history as-is (oldest -> newest)
        self._history = [dict(r) for r in historical_features]
        # engine expects DataFrame input for vectorized evaluation; we only need
        # it for rule-based signal generation per-row so it's ok to not precompute.
        # (No heavy computation here — safe.)
        return None

    def generate_signals(self, latest_features: Dict[str, Any]) -> List[Signal]:
        # append to history (keeps it if callers expect stateful behaviour)
        self._history.append(dict(latest_features))

        # Build a single-row DataFrame expected by rule engine
        df = pd.DataFrame([latest_features])
        out = self.engine.generate_signals(df)

        # engine returns DataFrame with 'signal' and optional named signals.
        # Convert the 'signal' column into 0/1/-1 and map to Signal objects.
        s_val = int(out.loc[0, "signal"]) if "signal" in out.columns else 0

        # If s_val == 0, return empty list (no action). If non-zero, create one Signal
        if s_val == 0:
            return []

        # Map sign to BUY/SELL as your system expects
        side = "BUY" if s_val > 0 else "SELL"
        size = float(self.rule_cfg.get("default_size", 1.0))

        sig = Signal(
            strategy_id=self.strategy_id,
            symbol=str(latest_features.get("symbol", "UNKNOWN")),
            side=side,
            size=size,
            score=float(out.loc[0].get(next((c for c in out.columns if c.startswith("buy") or c.startswith("sell")), "signal"), s_val)),
            meta={"rule_signal": s_val, "rule_columns": {c: out.loc[0, c] for c in out.columns if c.startswith("rule__")}}
        )
        return [sig]
