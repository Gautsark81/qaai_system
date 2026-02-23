# strategies/ise_probability_supercharged.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from strategies.strategy_base import (
    StrategyBase,
    StrategySignal,
    ScreeningResult,
    ContextProtocol,
)

# We reuse the existing tested ISE pieces
from strategies.ise_probability import (
    ISEProbabilityConfig,
    ISEProbabilityEngine,
)


# =====================================================================
#  CONFIG – 80%+ WIN-RATE MODE WITH SL / TP / TRAIL
# =====================================================================
@dataclass
class ISE80pConfig(ISEProbabilityConfig):
    """
    Extension of ISEProbabilityConfig for "80%+ win-rate mode".

    Adds risk/meta parameters but keeps compatibility with existing ISE engine.
    """

    # Override defaults to enforce high-probability mode
    min_win_prob: float = 0.80

    # ATR-based SL/TP (in ATR multiples)
    sl_atr_mult: float = 1.5     # e.g. 1.5 * ATR
    tp_atr_mult: float = 3.0     # e.g. 3.0 * ATR (R~2 vs SL)

    # Optional trailing-stop hint (in ATR multiples)
    trail_atr_mult: float = 1.0  # trailing distance from high/low, in ATR

    # Capital at risk per trade (for router / RM to interpret; purely meta here)
    max_risk_frac: float = 0.01  # 1% of equity per trade (hint, not enforced here)

    # If win_prob >= hard_mode_prob -> mark as "A+ / sniper" setup
    hard_mode_prob: float = 0.90

    # Optional cap on SL distance (in absolute index points)
    max_sl_points: Optional[float] = None

    # Optional cap on TP distance (in absolute index points)
    max_tp_points: Optional[float] = None

    # Flag to enable/disable "hard mode" filtering entirely
    enable_hard_mode: bool = True


# =====================================================================
#  SUPERCHARGED STRATEGY
# =====================================================================
class ISE80pStrategy(StrategyBase):
    """
    Supercharged ISE strategy built on top of the existing ISE engine.

    - Uses ISEProbabilityEngine for feature construction & win_prob.
    - Enforces 80%+ win_prob (configurable via ISE80pConfig.min_win_prob).
    - Emits StrategySignal with rich meta:
        * win_prob, screen_score, regime, atr, features
        * SL / TP / Trail distances (ATR & absolute price)
        * R-multiple / risk fraction hints

    NOTE:
        This file does NOT replace tests or the existing ISEProbabilityStrategy.
        It is a "production/live" strategy that you can attach to the
        ExecutionOrchestrator while keeping tests untouched.
    """

    def __init__(
        self,
        ise_config: Optional[ISE80pConfig] = None,
        engine: Optional[ISEProbabilityEngine] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Flexible construction:

        - ISE80pStrategy()                       -> default ISE80pConfig()
        - ISE80pStrategy(ise_config=ISE80pConfig(...))
        - ISE80pStrategy(config={...})          -> dict merged into ISE80pConfig
        """
        if ise_config is None:
            base = ISE80pConfig().__dict__.copy()
            if isinstance(config, dict):
                base.update(config)
            ise_config = ISE80pConfig(**base)

        # StrategyBase config is just the dict form (for logging/introspection)
        StrategyBase.__init__(self, config=ise_config.__dict__.copy())

        self.config80 = ise_config
        self.engine = engine or ISEProbabilityEngine(self.config80, ml_model=None)
        self.name = self.config80.name or "ISE_80P"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_entry_price(
        self,
        ctx: ContextProtocol,
        symbol: str,
        features: Dict[str, Any],
    ) -> float:
        """
        Best-effort entry price hint. We do *not* submit orders here; we just
        provide a clean number that router / execution can treat as the
        reference for SL/TP calculations.
        """
        # 1) Try feature snapshot prices
        for k in ("last_price", "close", "mid", "price"):
            if k in features and features[k] is not None:
                try:
                    val = float(features[k])
                    if val > 0:
                        return val
                except Exception:
                    continue

        # 2) Try context helpers if available
        for meth_name in ("get_last_price", "last_price", "get_price"):
            meth = getattr(ctx, meth_name, None)
            if callable(meth):
                try:
                    val = float(meth(symbol))
                    if val > 0:
                        return val
                except Exception:
                    continue

        # 3) Fallback to 1.0 (won't be used for actual routing, just meta)
        return 1.0

    def _apply_point_caps(
        self, distance: float, cap_points: Optional[float]
    ) -> float:
        if cap_points is None:
            return distance
        try:
            return min(float(distance), float(cap_points))
        except Exception:
            return distance

    # ------------------------------------------------------------------
    # MAIN: generate_signals
    # ------------------------------------------------------------------
    def generate_signals(
        self,
        ctx: ContextProtocol,
        screening_results: Dict[str, List[ScreeningResult]],
    ) -> List[StrategySignal]:
        cfg = self.config80
        if not cfg.enabled:
            return []

        # Watchlist filter
        wl_syms = set(ctx.watchlist(cfg.watchlist_name))
        if not wl_syms:
            return []

        # Flatten screener results
        all_results: List[ScreeningResult] = [
            r for lst in screening_results.values() for r in lst
        ]
        candidates = [r for r in all_results if r.symbol in wl_syms]

        # Sort by descending score (highest quality first)
        candidates.sort(key=lambda r: r.score, reverse=True)

        signals: List[StrategySignal] = []

        for r in candidates:
            if len(signals) >= cfg.max_positions:
                break

            fv = self.engine.build_features(ctx, r.symbol)
            if fv is None:
                continue

            win_prob = self.engine.predict_win_prob(fv)

            # Base probability filter (80% mode)
            if win_prob < cfg.min_win_prob:
                continue

            # Optional "hard mode": keep only A+ setups (win_prob >= hard_mode_prob)
            hard_mode_flag = False
            if cfg.enable_hard_mode and cfg.hard_mode_prob is not None:
                if win_prob >= float(cfg.hard_mode_prob):
                    hard_mode_flag = True
                else:
                    # Still allow non-hard-mode trades, but flag them
                    hard_mode_flag = False

            side = "BUY" if r.score >= 0 else "SELL"

            # VWAP bias alignment (same as engine strategy)
            bias = fv.meta.get("vwap_bias", 0.0)
            if cfg.use_vwap_bias:
                if side == "BUY" and bias < 0:
                    continue
                if side == "SELL" and bias > 0:
                    continue

            # ATR & volatility
            atr = float(fv.meta.get(cfg.atr_feature, fv.meta.get("atr", 1.0)) or 1.0)
            atr = max(atr, 1e-6)

            # Inverse-vol sizing, capped by max_per_symbol
            inv_vol = 1.0 / atr
            raw_size = min(cfg.max_per_symbol, inv_vol)

            # Entry price for SL/TP
            feats_main = ctx.get_feature_snapshot(r.symbol, cfg.timeframe) or {}
            entry_price = self._get_entry_price(ctx, r.symbol, feats_main)

            # Distances in price terms
            sl_dist_pts = cfg.sl_atr_mult * atr
            tp_dist_pts = cfg.tp_atr_mult * atr

            # Optional caps in absolute points
            sl_dist_pts = self._apply_point_caps(sl_dist_pts, cfg.max_sl_points)
            tp_dist_pts = self._apply_point_caps(tp_dist_pts, cfg.max_tp_points)

            if side == "BUY":
                sl_price = entry_price - sl_dist_pts
                tp_price = entry_price + tp_dist_pts
            else:
                sl_price = entry_price + sl_dist_pts
                tp_price = entry_price - tp_dist_pts

            # Basic R-multiple (TP / SL distance)
            try:
                r_mult = abs(tp_price - entry_price) / max(
                    abs(entry_price - sl_price), 1e-6
                )
            except Exception:
                r_mult = 0.0

            # Risk fraction hint (not enforced here; router/RM can use this)
            risk_frac_hint = cfg.max_risk_frac

            # Assemble meta (backwards-compatible keys preserved)
            meta: Dict[str, Any] = {
                # Core probability & screener info
                "win_prob": win_prob,
                "screen_score": r.score,
                "regime": fv.meta.get("regime"),
                "atr": atr,
                "features": fv.meta,
                # Entry & direction
                "entry_price_hint": entry_price,
                "side": side,
                # SL / TP / Trail
                "sl_atr_mult": cfg.sl_atr_mult,
                "tp_atr_mult": cfg.tp_atr_mult,
                "trail_atr_mult": cfg.trail_atr_mult,
                "sl_distance_pts": sl_dist_pts,
                "tp_distance_pts": tp_dist_pts,
                "sl_price_hint": sl_price,
                "tp_price_hint": tp_price,
                "r_multiple_hint": r_mult,
                # Risk envelope
                "max_risk_frac_hint": risk_frac_hint,
                "hard_mode": hard_mode_flag,
                # For router-side routing / logging
                "strategy_mode": "ISE_80P",
            }

            signals.append(
                StrategySignal(
                    strategy=cfg.name,
                    symbol=r.symbol,
                    side=side,
                    size=raw_size,
                    meta=meta,
                )
            )

        return signals
