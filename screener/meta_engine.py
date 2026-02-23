# qaai_system/screener/meta_engine.py
from __future__ import annotations
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
import time

from qaai_system.screener.feature_extractor import FeatureExtractor
from .engine import ScreeningEngineSupercharged
from .feedback import ScreenerFeedback
from .explainability import ExplainabilityLogger


class MetaScreeningEngine:
    """
    Polished, adaptive screening meta-engine.

    Features:
      - ensemble fusion over rule + ml + timeframe-consistency
      - dynamic weight adaptation based on recent performance
      - self-healing blacklist (auto-exclude repeatedly failing symbols)
      - multi-timeframe check (short + mid windows)
      - explainability snapshots recorded per run
    """

    def __init__(
        self,
        base_engine: Optional[ScreeningEngineSupercharged] = None,
        feedback: Optional[ScreenerFeedback] = None,
        explain_logger: Optional[ExplainabilityLogger] = None,
        w_rule: float = 0.5,
        w_ml: float = 0.5,
        adapt_alpha: float = 0.05,
        blacklist_threshold: int = 3,
        blacklist_ttl_seconds: int = 60 * 60,
        min_score_threshold: float = 0.0,
        timeframe_short: int = 5,
        timeframe_mid: int = 20,
    ):
        self.engine = base_engine or ScreeningEngineSupercharged(
            w_rule=w_rule, w_ml=w_ml, feedback=feedback, explain_logger=explain_logger
        )
        self.feedback = feedback or ScreenerFeedback()
        self.explain = explain_logger or ExplainabilityLogger()
        self.w_rule = float(w_rule)
        self.w_ml = float(w_ml)
        self.adapt_alpha = float(adapt_alpha)
        self.blacklist_threshold = int(blacklist_threshold)
        self.blacklist_ttl_seconds = int(blacklist_ttl_seconds)
        self.min_score_threshold = float(min_score_threshold)
        self.timeframe_short = int(timeframe_short)
        self.timeframe_mid = int(timeframe_mid)

        self.symbol_fail_counts: Dict[str, int] = {}
        self.blacklist: Dict[str, float] = {}
        self.performance_window: List[Tuple[str, float]] = []
        self._last_run_ts = 0.0

    # -------------------------
    # Blacklist helpers
    # -------------------------
    def _is_blacklisted(self, symbol: str) -> bool:
        now = time.time()
        exp = self.blacklist.get(symbol)
        if exp is None:
            return False
        if exp < now:
            self.blacklist.pop(symbol, None)
            self.symbol_fail_counts.pop(symbol, None)
            return False
        return True

    def _register_failure(self, symbol: str):
        cnt = self.symbol_fail_counts.get(symbol, 0) + 1
        self.symbol_fail_counts[symbol] = cnt
        if cnt >= self.blacklist_threshold:
            self.blacklist[symbol] = time.time() + self.blacklist_ttl_seconds

    def _register_success(self, symbol: str):
        if symbol in self.symbol_fail_counts:
            self.symbol_fail_counts[symbol] = max(
                0, self.symbol_fail_counts[symbol] - 1
            )

    # -------------------------
    # Weight adaptors
    # -------------------------
    def adapt_weights_from_feedback(self):
        if not self.performance_window:
            return
        ml_effect, rule_effect, count = 0.0, 0.0, 0
        for sym, realized in self.performance_window:
            fb = self.feedback.get(sym)
            ml_effect += realized * (fb - 1.0)
            rule_effect += realized * (1.0 / (fb + 1e-9) - 1.0)
            count += 1
        if count == 0:
            return
        ml_effect /= count
        rule_effect /= count
        diff = ml_effect - rule_effect
        self.w_ml = float(min(0.95, max(0.05, self.w_ml + self.adapt_alpha * diff)))
        self.w_rule = float(max(0.05, 1.0 - self.w_ml))
        self.performance_window.clear()

    # -------------------------
    # Multi-timeframe consistency
    # -------------------------
    def _multi_timeframe_multiplier(self, full_df: pd.DataFrame, symbol: str) -> float:
        sdf = full_df[full_df["symbol"] == symbol].copy()
        if sdf.empty:
            return 0.0
        short_len = min(len(sdf), self.timeframe_short)
        mid_len = min(len(sdf), self.timeframe_mid)
        if short_len < 2 or mid_len < 2:
            return 1.0

        short_mom = (sdf["close"].iloc[-1] / sdf["close"].iloc[-short_len]) - 1.0
        mid_mom = (sdf["close"].iloc[-1] / sdf["close"].iloc[-mid_len]) - 1.0

        # Conflicting momentum → reject completely
        if short_mom * mid_mom < 0:
            self._register_failure(symbol)
            return 0.0  # guaranteed fail

        # Tiny/noisy moves → reject entirely
        tiny_thresh = 0.002
        if abs(short_mom) < tiny_thresh or abs(mid_mom) < tiny_thresh:
            return 0.0  # severe penalty

        return 1.0

    # -------------------------
    # Main screening run
    # -------------------------
    def run_cycle(
        self,
        market_df: pd.DataFrame,
        top_k: int = 50,
        score_threshold: Optional[float] = None,
    ) -> List[Tuple[str, float]]:
        if score_threshold is None:
            score_threshold = self.min_score_threshold

        candidates = market_df[
            ~market_df["symbol"].isin(
                [s for s in list(self.blacklist.keys()) if self._is_blacklisted(s)]
            )
        ].copy()

        dfe = self.engine
        base_results = dfe.screen(candidates, top_k=top_k * 3)

        latest = (
            FeatureExtractor.compute_all(candidates)
            .groupby("symbol")
            .tail(1)
            .reset_index(drop=True)
        )
        feats_cols = ["ADV20", "ATR14", "MOM10", "VOL10"]
        X = latest[feats_cols].fillna(0).values
        ml_probs = (
            dfe.classifier.predict_proba(X)[:, 1]
            if hasattr(dfe.classifier, "predict_proba")
            else np.repeat(0.5, len(latest))
        )
        symbol_to_ml = dict(zip(latest["symbol"], ml_probs))

        symbol_to_rule = {}
        for _, row in latest.iterrows():
            symbol_to_rule[row["symbol"]] = dfe._compute_rule_score(row)

        scored: List[Tuple[str, float]] = []
        for sym in latest["symbol"].tolist():
            if self._is_blacklisted(sym):
                continue
            ml_score = float(symbol_to_ml.get(sym, 0.5))
            rule_score = float(symbol_to_rule.get(sym, 0.0))
            fb = self.feedback.get(sym)
            meta_score = (self.w_rule * rule_score + self.w_ml * ml_score) * fb
            multiplier = self._multi_timeframe_multiplier(market_df, sym)
            meta_score *= multiplier
            scored.append((sym, float(meta_score)))

        scored.sort(key=lambda x: x[1], reverse=True)
        filtered = [(s, sc) for s, sc in scored if sc >= score_threshold]
        result = filtered[:top_k]

        for sym, sc in result:
            row = latest[latest["symbol"] == sym].iloc[0].to_dict()
            self.explain.log(
                sym,
                str(row.get("timestamp")),
                {
                    "meta_w_rule": self.w_rule,
                    "meta_w_ml": self.w_ml,
                    "rule_score": symbol_to_rule.get(sym),
                    "ml_score": symbol_to_ml.get(sym),
                    "feedback": self.feedback.get(sym),
                    "timeframe_short": self.timeframe_short,
                    "timeframe_mid": self.timeframe_mid,
                },
                sc,
                reason="meta_ensemble",
            )

        self._last_run_ts = time.time()
        return result

    # -------------------------
    # Post-trade feedback hooks
    # -------------------------
    def on_trade_closed(self, symbol: str, realized_pnl: float, notional: float):
        new_w = self.feedback.update(symbol, realized_pnl, notional)
        self.performance_window.append((symbol, realized_pnl / max(notional, 1e-9)))
        if realized_pnl < 0:
            self._register_failure(symbol)
        else:
            self._register_success(symbol)
        if len(self.performance_window) >= 10:
            self.adapt_weights_from_feedback()

    def manual_unblacklist(self, symbol: str):
        self.blacklist.pop(symbol, None)
        self.symbol_fail_counts.pop(symbol, None)
