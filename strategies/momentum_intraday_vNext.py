"""
Momentum Intraday – Hybrid AI/ML + Neuro-Symbolic + Self-Adaptive Strategy
Phase 3 (AMATS Evolution Engine)

This module upgrades the original MomentumIntradayStrategy into a
futuristic, production-ready autonomous decision system:

- Regime-adaptive momentum logic
- Optional ML prediction plug-ins (deep learning, meta-learning)
- RL-based dynamic position sizing
- Neuro-symbolic expert fusion (rules + ML confidence)
- Self-healing and self-evolving parameter framework
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from screening.results import ScreeningResult
from strategies.base import Strategy, StrategyConfig, StrategyContext, StrategySignal
import math


# ======================================================================
# CONFIG: Fully future-proof & plug-in extensible
# ======================================================================
@dataclass(slots=True)
class MomentumIntradayVNextConfig(StrategyConfig):
    """
    Next-generation intraday momentum configuration.

    This stays StrategyConfig-compatible so it can be wired into the
    same orchestration / registry you use for all strategies.
    """

    # Core
    min_score: float = 0.0
    timeframe: str = "1m"
    watchlist_name: str = "DAY_SCALP"

    # --- Hybrid AI / ML Support ---
    use_ml: bool = False
    ml_predict_fn: Optional[Callable[[str, Dict[str, float]], float]] = None
    # e.g. fn(symbol, feature_vector_dict) -> float in [-1, +1] where
    # positive => higher confidence, negative => lower confidence

    use_rl_sizer: bool = False
    rl_sizer_fn: Optional[Callable[[StrategyContext, float], float]] = None
    # e.g. fn(context, raw_size) -> adjusted_size

    # --- Regime Adaptation ---
    regime_feature: str = "rsi"
    bull_threshold: float = 55.0
    bear_threshold: float = 45.0

    # --- Evolution / adaptation ---
    auto_evolve: bool = True
    evolve_lr: float = 0.01  # how fast parameters adapt from live feedback

    # --- Maximum risk limits ---
    max_per_symbol: float = 1.0
    max_positions: int = 10


# ======================================================================
# MAIN STRATEGY
# ======================================================================
class MomentumIntradayVNext(Strategy):
    """
    Production-grade, self-adaptive intraday momentum strategy.

    It is *signal-level* (generate_signals), intended to sit on top of
    your screening + feature-store stack and feed the routing layer
    with sized momentum signals.
    """

    def __init__(self, config: MomentumIntradayVNextConfig):
        super().__init__(config=config)
        self.config = config

        # Evolutionary parameter containers (self-healing core)
        self.param_memory: Dict[str, float] = {
            "min_score": float(config.min_score),
            "bull_mult": 1.0,
            "bear_mult": 1.0,
        }

    # ------------------------------------------------------------------
    # SELF-HEALING MECHANISM: adjust parameters automatically
    # after each trading session or based on rolling accuracy.
    # ------------------------------------------------------------------
    def evolve_parameters(self, ctx: StrategyContext, pnl: float) -> None:
        """
        Self-healing parameter update.

        Call this with realized PnL (e.g., end-of-day) to slowly adapt
        aggressiveness and score thresholds.
        """
        if not self.config.auto_evolve:
            return

        # Scale pnl into [-1, 1] using tanh to avoid explosions.
        delta = math.tanh(float(pnl) / 10_000.0)
        lr = float(self.config.evolve_lr)

        # Small adaptive updates
        self.param_memory["min_score"] -= delta * lr
        self.param_memory["bull_mult"] += delta * lr
        self.param_memory["bear_mult"] -= delta * lr

        # Hard boundaries
        self.param_memory["min_score"] = max(
            -1.0, min(1.0, self.param_memory["min_score"])
        )
        self.param_memory["bull_mult"] = max(
            0.5, min(2.0, self.param_memory["bull_mult"])
        )
        self.param_memory["bear_mult"] = max(
            0.5, min(2.0, self.param_memory["bear_mult"])
        )

        ctx.log_meta(
            "strategy_evolution",
            {"updated_params": dict(self.param_memory), "pnl_feedback": float(pnl)},
        )

    # ------------------------------------------------------------------
    # Regime classifier: symbolic logic + feature database
    # ------------------------------------------------------------------
    def detect_regime(self, feats: Dict) -> str:
        """
        Very simple RSI-based regime detector.

        - rsi >= bull_threshold  -> "bull"
        - rsi <= bear_threshold  -> "bear"
        - otherwise              -> "neutral"
        """
        try:
            rsi = float(feats.get(self.config.regime_feature, 50.0))
        except (TypeError, ValueError):
            rsi = 50.0

        if rsi >= self.config.bull_threshold:
            return "bull"
        if rsi <= self.config.bear_threshold:
            return "bear"
        return "neutral"

    # ------------------------------------------------------------------
    # ML prediction fusion – returns confidence multiplier in [0.5, 2]
    # ------------------------------------------------------------------
    def ml_confidence(self, symbol: str, feats: Dict) -> float:
        """
        Convert an arbitrary ML prediction into a stable multiplier
        in [0.5, 2.0]. If ML is disabled or fails, returns 1.0.
        """
        if not self.config.use_ml or not self.config.ml_predict_fn:
            return 1.0

        try:
            pred_raw = float(self.config.ml_predict_fn(symbol, feats))
        except Exception:
            return 1.0

        # Map arbitrary prediction into [-1, +1] then into [0.5, 2.0]
        pred_clip = max(-1.0, min(1.0, pred_raw))
        return max(0.5, min(2.0, 1.0 + pred_clip))

    # ------------------------------------------------------------------
    # RL-based position sizer
    # ------------------------------------------------------------------
    def rl_sizer(self, ctx: StrategyContext, raw: float) -> float:
        """
        Optional RL-based sizer hook. If not configured, returns raw.
        """
        if not self.config.use_rl_sizer or not self.config.rl_sizer_fn:
            return float(raw)
        try:
            return float(self.config.rl_sizer_fn(ctx, float(raw)))
        except Exception:
            # Fail gracefully: never let sizing crash the strategy.
            return float(raw)

    # ------------------------------------------------------------------
    # MAIN SIGNAL GENERATION
    # ------------------------------------------------------------------
    def generate_signals(
        self,
        ctx: StrategyContext,
        screening_results: Dict[str, List[ScreeningResult]],
    ) -> List[StrategySignal]:
        """
        Core entry point: convert screening results into StrategySignal objects.

        This function is intentionally deterministic given (ctx, screening_results)
        and all state in self.param_memory.
        """
        if not self.config.enabled:
            return []

        wl = set(ctx.watchlist(self.config.watchlist_name))
        if not wl:
            return []

        # Combine all screener results into a single list
        all_results: List[ScreeningResult] = [
            r for lst in screening_results.values() for r in lst
        ]

        # Dynamic score threshold (evolving min_score)
        min_score_dyn = float(self.param_memory.get("min_score", self.config.min_score))
        hard_floor = float(self.config.min_score)

        filtered = [
            r
            for r in all_results
            if r.symbol in wl and r.score >= max(hard_floor, min_score_dyn)
        ]

        # Sort by descending score (strongest momentum first)
        filtered.sort(key=lambda r: r.score, reverse=True)

        signals: List[StrategySignal] = []

        for r in filtered[: self.config.max_positions]:
            feats = ctx.get_feature_snapshot(r.symbol, self.config.timeframe) or {}

            # Defensive ATR extraction
            try:
                vol = float(feats.get("atr", 1.0))
            except (TypeError, ValueError):
                vol = 1.0

            vol = max(vol, 1e-6)
            inv_vol = 1.0 / vol

            regime = self.detect_regime(feats)
            ml_mult = self.ml_confidence(r.symbol, feats)

            # Regime multipliers
            if regime == "bull":
                regime_mult = float(self.param_memory["bull_mult"])
            elif regime == "bear":
                regime_mult = float(self.param_memory["bear_mult"])
            else:
                regime_mult = 1.0

            # Raw size engine: inverse volatility * ML * regime
            raw = inv_vol * ml_mult * regime_mult
            # Cap by per-symbol maximum risk
            raw = min(self.config.max_per_symbol, raw)

            # RL execution agent adjusts this further
            sized = self.rl_sizer(ctx, raw)

            # Final guard
            sized = max(0.0, float(sized))
            if sized <= 0.0:
                continue

            side = "BUY" if r.score >= 0 else "SELL"

            signals.append(
                StrategySignal(
                    strategy=self.config.name,
                    symbol=r.symbol,
                    side=side,
                    size=float(sized),
                    meta={
                        "screen_score": float(r.score),
                        "regime": regime,
                        "ml_mult": ml_mult,
                        "regime_mult": regime_mult,
                        "vol": vol,
                        "inv_vol": inv_vol,
                        "evolved_params": dict(self.param_memory),
                        "min_score_effective": max(hard_floor, min_score_dyn),
                    },
                )
            )

        return signals
