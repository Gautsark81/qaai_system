"""
Example strategies for orchestrator integration and portfolio simulation.

MASTER UPGRADE OBJECTIVES:
🧠 Multi-strategy registry (intraday vs swing).
📊 Risk-aware allocations (uses account equity).
⚡ Compatible with PortfolioManager aggregation & netting.
🎯 Bracket-ready (plans carry optional bracket hints).
🔄 Feedback-ready (on_feedback hooks for reinforcement / logging).
🔌 Orchestrator-safe (produces plain order plan dicts).
"""

from typing import Dict, Any, List, Optional
import random
import math


class BaseStrategy:
    """Minimal strategy base class for orchestration & testing."""

    def __init__(self, name: str, max_alloc_pct: float = 0.05):
        """
        :param name: strategy identifier
        :param max_alloc_pct: maximum fraction of account equity to allocate to a single trade
        """
        self.name = name
        self.max_alloc_pct = float(max_alloc_pct)
        self.history: List[Dict[str, Any]] = []

    def generate_plan(
        self, snapshot: Dict[str, Any], account_equity: float
    ) -> List[Dict[str, Any]]:
        """Return list of order plans (possibly empty). Implemented by subclasses."""
        raise NotImplementedError

    def on_feedback(self, trade: Dict[str, Any]) -> None:
        """Record feedback (trade closed / pnl) for learning/analysis."""
        self.history.append(trade)

    def _qty_from_alloc(
        self, price: float, account_equity: float, alloc_pct: Optional[float] = None
    ) -> int:
        pct = self.max_alloc_pct if alloc_pct is None else float(alloc_pct)
        if price <= 0:
            return 0
        qty = (account_equity * pct) / price
        return max(0, int(math.floor(qty)))


class IntradayMomentumStrategy(BaseStrategy):
    """
    Intraday momentum / breakout style.

    - Very short timeframe (intraday).
    - Uses snapshot['signal'] (buy/sell/hold) if present; otherwise random lightweight signal for tests.
    - Sizing is conservative by default (small max_alloc_pct).
    - Produces an optional bracket hint (take_profit_pct, stop_loss_pct) for PortfolioManager/BracketManager to use.
    """

    def __init__(self, symbol: str, max_alloc_pct: float = 0.03):
        super().__init__(name="intraday_momentum", max_alloc_pct=max_alloc_pct)
        self.symbol = symbol

    def generate_plan(
        self, snapshot: Dict[str, Any], account_equity: float
    ) -> List[Dict[str, Any]]:
        price = float(snapshot.get("price", 100.0) or 100.0)
        atr = float(snapshot.get("atr", 1.0) or 1.0)
        # explicit signal preferred for deterministic tests
        signal = snapshot.get("signal")
        if signal is None:
            # fallback random minor bias
            signal = random.choice(["buy", "sell", "hold"])

        if signal == "hold":
            return []

        qty = self._qty_from_alloc(price, account_equity)
        if qty <= 0:
            return []

        # produce conservative intraday bracket hints
        tp_pct = snapshot.get("intraday_tp_pct", 0.02)  # 2% default
        sl_pct = snapshot.get("intraday_sl_pct", 0.01)  # 1% default

        plan = {
            "strategy": self.name,
            "symbol": self.symbol,
            "side": signal,
            "quantity": qty,
            "price": price,
            "atr": atr,
            "timeframe": "intraday",
            # bracket hint for PortfolioManager/Orchestrator to attach (optional)
            "bracket": {
                "take_profits": [{"pct": tp_pct * 100, "qty_frac": 1.0}],
                "stop": {"type": "percent", "trail_pct": sl_pct * 100},
            },
            "meta": {"confidence": 0.6},
        }
        return [plan]


class SwingReversalStrategy(BaseStrategy):
    """
    Swing reversal (contrarian) strategy.

    - Multi-day horizon.
    - Acts on snapshot['change_pct'] (if present).
    - Uses larger allocation than intraday by default.
    """

    def __init__(self, symbol: str, max_alloc_pct: float = 0.08):
        super().__init__(name="swing_reversal", max_alloc_pct=max_alloc_pct)
        self.symbol = symbol

    def generate_plan(
        self, snapshot: Dict[str, Any], account_equity: float
    ) -> List[Dict[str, Any]]:
        price = float(snapshot.get("price", 100.0) or 100.0)
        atr = float(snapshot.get("atr", 1.0) or 1.0)
        change_pct = float(snapshot.get("change_pct", 0.0) or 0.0)

        # skip small moves
        if abs(change_pct) < 0.01:
            return []

        # contrarian: sell on big upmove, buy on big downmove
        side = "sell" if change_pct > 0 else "buy"

        qty = self._qty_from_alloc(price, account_equity)
        if qty <= 0:
            return []

        # swing bracket hints are wider
        tp_pct = snapshot.get("swing_tp_pct", 0.06)  # 6%
        sl_pct = snapshot.get("swing_sl_pct", 0.04)  # 4%

        plan = {
            "strategy": self.name,
            "symbol": self.symbol,
            "side": side,
            "quantity": qty,
            "price": price,
            "atr": atr,
            "timeframe": "swing",
            "bracket": {
                "take_profits": [{"pct": tp_pct * 100, "qty_frac": 1.0}],
                "stop": {"type": "percent", "trail_pct": sl_pct * 100},
            },
            "meta": {"confidence": 0.55, "change_pct": change_pct},
        }
        return [plan]

    def on_trade_result(self, trade: Dict[str, Any]) -> None:
        """
        Optional hook called by PortfolioManager.record_trade_result when a trade
        related to this strategy closes. `trade` contains keys: symbol, pnl, qty.
        Implementations may update internal counters / performance stats.
        """
        try:
            if not hasattr(self, "_perf"):
                self._perf = {"pnl": 0.0, "trades": 0}
            self._perf["pnl"] += float(trade.get("pnl", 0.0) or 0.0)
            self._perf["trades"] += 1
            # Keep a tiny log
            # self.logger.info({"evt":"strategy_trade_feedback", "strategy": self.id, "trade": trade})
        except Exception:
            # never raise
            pass
