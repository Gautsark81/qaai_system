# execution/trade_classifier.py
import pandas as pd
from datetime import datetime, time
from zoneinfo import ZoneInfo
from typing import Literal, Optional, Any

IST = ZoneInfo("Asia/Kolkata")
TradeType = Literal["INTRADAY", "SWING"]


class TradeClassifier:
    """
    Classifies trade type (INTRADAY or SWING) and provides time-based entry/exit checks.
    Backwards-compatible signatures for tests:
      - classify_trade(entry_time=None, volatility=None, trend_strength=None, **kwargs)
      - is_entry_allowed(trade_type, entry_time=None)
      - should_force_exit(trade_type, current_time=None)
    """

    def __init__(
        self, ml_model: Optional[Any] = None, volatility_threshold: float = 1.0
    ):
        self.ml_model = ml_model
        self.volatility_threshold = volatility_threshold

        # Intraday trading rules (IST times)
        self.intraday_start = time(9, 30)
        self.intraday_last_entry = time(14, 45)
        self.intraday_force_exit = time(15, 15)

    def classify_trade(
        self,
        entry_time: Optional[datetime] = None,
        volatility: Optional[float] = None,
        trend_strength: Optional[float] = None,
        **kwargs
    ) -> TradeType:
        """
        Determine trade type. If ml_model provided, attempt to use it.
        Otherwise rule-based: entries during intraday window -> INTRADAY, else SWING.
        Accepts optional volatility and trend_strength for rule adjustments.
        """
        now = entry_time or datetime.now(IST)
        if now.tzinfo is None:
            now = now.replace(tzinfo=IST)

        # ML fallback
        if self.ml_model:
            try:
                features = {
                    "hour": now.hour,
                    "minute": now.minute,
                    "volatility": float(volatility or 0.0),
                    "trend_strength": float(trend_strength or 0.0),
                }
                pred = self.ml_model.predict([features])[0]
                if pred in ("INTRADAY", "SWING"):
                    return pred
            except Exception:
                # silent fallback to rule-based
                pass

        # Rule-based
        if self.intraday_start <= now.time() <= self.intraday_last_entry:
            return "INTRADAY"
        return "SWING"

    def is_entry_allowed(
        self, trade_type: TradeType, entry_time: Optional[datetime] = None
    ) -> bool:
        """
        Return whether entry is allowed. For intraday, enforce last entry cutoff.
        """
        now = entry_time or datetime.now(IST)
        if now.tzinfo is None:
            now = now.replace(tzinfo=IST)

        if trade_type == "INTRADAY":
            return self.intraday_start <= now.time() <= self.intraday_last_entry
        return True

    def should_force_exit(
        self, trade_type: TradeType, current_time: Optional[datetime] = None
    ) -> bool:
        """
        Force-close intraday trades after force-exit time.
        """
        now = current_time or datetime.now(IST)
        if now.tzinfo is None:
            now = now.replace(tzinfo=IST)

        if trade_type == "INTRADAY" and now.time() >= self.intraday_force_exit:
            return True
        return False


def bulk_classify(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Batch classify trades into WIN/LOSS/BREAKEVEN using 'pnl' column.
    Adds 'classification' column to returned DataFrame.
    """
    if not isinstance(trades_df, pd.DataFrame):
        raise ValueError("trades_df must be a pandas DataFrame")

    if "pnl" not in trades_df.columns:
        # If PnL isn't present, classify as 'UNKNOWN'
        out = trades_df.copy()
        out["classification"] = "UNKNOWN"
        return out

    out = trades_df.copy()
    out["classification"] = out["pnl"].apply(
        lambda p: "WIN" if p > 0 else ("LOSS" if p < 0 else "BREAKEVEN")
    )
    return out
