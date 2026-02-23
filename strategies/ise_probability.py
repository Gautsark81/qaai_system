from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple

from screening.results import ScreeningResult
from strategies.base import StrategyBase


# =====================================================================
#  Context protocol (for type hints only, not required at runtime)
# =====================================================================
class ContextProtocol(Protocol):
    def watchlist(self, name: str) -> List[str]: ...
    def get_feature_snapshot(self, symbol: str, timeframe: str) -> Dict[str, Any]: ...
    def get_l2_snapshot(self, symbol: str) -> Dict[str, Any]: ...
    def get_vwap(self, symbol: str, timeframe: str) -> float: ...
    def get_anchored_vwap(self, symbol: str, anchor_id: str) -> float: ...


# =====================================================================
#  StrategySignal (local, lightweight)
# =====================================================================
@dataclass
class StrategySignal:
    """
    Lightweight signal object emitted by ISEProbabilityStrategy.

    NOTE: This is a *signal*-level abstraction. Your router/execution
    layer is responsible for mapping this into actual orders and for
    turning SL/TP hints in meta into concrete price levels.
    """
    strategy: str
    symbol: str
    side: str        # "BUY" or "SELL"
    size: float
    meta: Dict[str, Any]


# =====================================================================
#  ML model protocol (sklearn/LightGBM-style adapter)
# =====================================================================
class OnlineProbModel(Protocol):
    """
    Minimal protocol for an online probability model.

    Implementations may wrap:
      - sklearn.linear_model.SGDClassifier
      - LightGBM wrapper
      - custom online learner

    Required API:
      - predict_proba([feature_vector]) -> [[p0, p1]]
      - partial_fit([feature_vector], [label], classes=[0,1])
    """

    def predict_proba(self, X: List[List[float]]) -> List[List[float]]:
        ...

    def partial_fit(
        self,
        X: List[List[float]],
        y: List[int],
        classes: List[int],
        sample_weight: Optional[List[float]] = None,
    ) -> None:
        ...


# =====================================================================
#  CONFIG
# =====================================================================
@dataclass
class ISEProbabilityConfig:
    """
    Config for ISE "80%+ win rate mode" probability strategy.
    """

    name: str = "ISE_PROB"
    enabled: bool = True

    timeframe: str = "1m"
    higher_timeframes: Tuple[str, str] = ("5m", "15m")
    watchlist_name: str = "DAY_SCALP"

    # Probability threshold for taking trades
    min_win_prob: float = 0.75  # 0.75–0.85 is typical target

    # Feature toggles
    use_l2: bool = True               # use L2/order-book features
    use_ob_fvg: bool = True           # order-block / FVG features
    use_vwap_bias: bool = True        # VWAP + anchored VWAP
    use_mtfa_filter: bool = True      # 1m + 5m + 15m confluence
    use_ml_confidence: bool = True    # use ML model if available

    # Regime + risk
    regime_feature: str = "regime"    # or derive from trend/vol
    atr_feature: str = "atr"
    max_per_symbol: float = 1.0
    max_positions: int = 5

    # Online ML model (optional)
    ml_enabled: bool = False
    ml_min_conf_samples: int = 100    # minimum trades before trusting ML strongly

    # Execution / risk hints (actual enforcement is in risk & router)
    kelly_fraction: float = 0.02      # fraction of equity per trade
    max_dd_soft: float = 0.10         # 10% soft throttle
    max_dd_hard: float = 0.15         # 15% kill-switch hint

    # -----------------------------------------------------------------
    # SL / TP / Trailing hints (in ATR units)
    # These are *meta* hints for downstream execution, not enforced here.
    # -----------------------------------------------------------------
    sl_atr_mult: float = 1.5          # SL distance = sl_atr_mult * ATR
    tp_atr_mult: float = 1.0          # TP distance = tp_atr_mult * ATR
    breakeven_after_r: float = 0.7    # move SL to BE after 0.7R
    trail_after_r: float = 1.0        # start trailing after 1R
    trail_atr_mult: float = 1.0       # trailing distance = trail_atr_mult * ATR


# =====================================================================
#  FEATURE ENGINE
# =====================================================================
@dataclass
class ISEFeatureVector:
    """
    Compact feature struct for a candidate trade.
    """
    x: List[float]
    meta: Dict[str, Any]


class ISEProbabilityEngine:
    """
    Builds feature vectors for ISE and computes win-probability.

    Combines:
      - Liquidity sweeps & order blocks / FVG zones (pattern flags)
      - L2 imbalance & volume delta
      - VWAP / anchored VWAP bias
      - Multi-timeframe confirmation flags
      - Regime features (trend/chop/mean-reversion)
    """

    def __init__(
        self,
        config: ISEProbabilityConfig,
        ml_model: Optional[OnlineProbModel] = None,
    ) -> None:
        self.config = config
        self.ml_model = ml_model
        self._seen_samples = 0

    # ----------------- PUBLIC API -----------------
    def build_features(
        self,
        ctx: ContextProtocol,
        symbol: str,
    ) -> Optional[ISEFeatureVector]:
        tf = self.config.timeframe
        f_main = ctx.get_feature_snapshot(symbol, tf) or {}

        # 1) L2 / order-book features
        l2_imbalance = 0.0
        vol_delta = 0.0
        if self.config.use_l2:
            try:
                l2 = ctx.get_l2_snapshot(symbol) or {}
            except Exception:
                l2 = {}
            l2_imbalance, vol_delta = self._compute_l2_features(l2)

        # 2) Liquidity sweep + OB/FVG pattern flags (from feature store)
        sweep_flag = float(f_main.get("liq_sweep", 0.0))
        ob_flag = float(f_main.get("order_block", 0.0))
        fvg_flag = float(f_main.get("fvg", 0.0))

        # 3) VWAP bias & anchored VWAP
        vwap_bias = 0.0
        anchored_bias = 0.0
        if self.config.use_vwap_bias:
            vwap_bias = self._compute_vwap_bias(ctx, symbol, tf, f_main)
            anchored_bias = self._compute_anchored_vwap_bias(ctx, symbol, f_main)

        # 4) Multi-timeframe alignment
        mtf_agree = 1.0 if self._mtf_alignment(ctx, symbol) else 0.0

        # 5) Regime
        regime = f_main.get(self.config.regime_feature, "unknown")
        regime_onehot = self._regime_onehot(str(regime))

        # 6) ATR / volatility
        atr = float(f_main.get(self.config.atr_feature, 1.0))

        # Build numerical vector
        x: List[float] = []
        x.extend(regime_onehot)  # trend, meanrev, chop flags
        x.extend(
            [
                l2_imbalance,
                vol_delta,
                sweep_flag,
                ob_flag,
                fvg_flag,
                vwap_bias,
                anchored_bias,
                mtf_agree,
                1.0 / max(atr, 1e-6),
            ]
        )

        meta = {
            "regime": regime,
            "atr": atr,
            "liq_sweep": sweep_flag,
            "order_block": ob_flag,
            "fvg": fvg_flag,
            "vwap_bias": vwap_bias,
            "anchored_bias": anchored_bias,
            "mtf_agree": mtf_agree,
            "l2_imbalance": l2_imbalance,
            "vol_delta": vol_delta,
        }
        return ISEFeatureVector(x=x, meta=meta)

    def predict_win_prob(self, fv: ISEFeatureVector) -> float:
        """
        If ML model is available, use predict_proba.
        Otherwise, fall back to a handcrafted probability mapping
        that encodes the described edge sources.
        """
        if (
            self.config.use_ml_confidence
            and self.config.ml_enabled
            and self.ml_model is not None
            and self._seen_samples >= self.config.ml_min_conf_samples
        ):
            try:
                proba = self.ml_model.predict_proba([fv.x])[0]
                # label 1 = win
                return float(proba[1])
            except Exception:
                pass  # fall through

        # Handcrafted pseudo-probability:
        p = 0.5
        m = fv.meta

        # Liquidity sweep entry ~ +0.20
        if m["liq_sweep"] > 0:
            p += 0.20

        # OB/FVG sniper entries ~ +0.15 (combined, capped)
        ob_fvg = m["order_block"] + m["fvg"]
        p += 0.075 * min(ob_fvg, 2.0)

        # VWAP bias lock ~ +0.10
        p += 0.10 * m["vwap_bias"]

        # Anchored VWAP confirmation ~ +0.05
        p += 0.05 * m["anchored_bias"]

        # Multi-timeframe alignment ~ +0.10
        p += 0.10 * m["mtf_agree"]

        # Bound probability
        p = max(0.05, min(0.95, p))
        return p

    def update_with_outcome(self, fv: ISEFeatureVector, outcome_win: bool) -> None:
        """
        Online learning hook: call this after a trade is closed with known PnL.
        """
        if not (self.config.ml_enabled and self.ml_model is not None):
            return
        y = [1 if outcome_win else 0]
        try:
            self.ml_model.partial_fit([fv.x], y, classes=[0, 1])
            self._seen_samples += 1
        except Exception:
            return

    # ----------------- INTERNAL HELPERS -----------------
    def _compute_l2_features(self, l2: Dict[str, Any]) -> Tuple[float, float]:
        bid_vol = float(l2.get("bid_volume", 0.0))
        ask_vol = float(l2.get("ask_volume", 0.0))
        denom = max(bid_vol + ask_vol, 1e-6)
        imbalance = (bid_vol - ask_vol) / denom

        vol_delta = float(l2.get("buy_volume_delta", 0.0)) - float(
            l2.get("sell_volume_delta", 0.0)
        )
        return float(imbalance), float(vol_delta)

    def _compute_vwap_bias(
        self,
        ctx: ContextProtocol,
        symbol: str,
        timeframe: str,
        feats: Dict[str, Any],
    ) -> float:
        price = float(feats.get("close", feats.get("last_price", 0.0)))
        vwap = None
        try:
            vwap = ctx.get_vwap(symbol, timeframe)
        except Exception:
            vwap = feats.get("vwap")
        if not vwap:
            return 0.0
        vwap_val = float(vwap)
        if price > vwap_val:
            return 1.0
        if price < vwap_val:
            return -1.0
        return 0.0

    def _compute_anchored_vwap_bias(
        self,
        ctx: ContextProtocol,
        symbol: str,
        feats: Dict[str, Any],
    ) -> float:
        anchor_id = feats.get("sweep_anchor_id") or feats.get("ob_anchor_id")
        if not anchor_id:
            return 0.0
        try:
            avwap = ctx.get_anchored_vwap(symbol, anchor_id)
        except Exception:
            return 0.0
        price = float(feats.get("close", feats.get("last_price", 0.0)))
        avwap_val = float(avwap)
        if price > avwap_val:
            return 1.0
        if price < avwap_val:
            return -1.0
        return 0.0

    def _mtf_alignment(self, ctx: ContextProtocol, symbol: str) -> bool:
        """
        Returns True if all *non-zero* trend signs across 1m + higher
        timeframes agree in direction, and at least one is non-zero.

        This matches the test expectation that:
          - 1m neutral, 5m + 15m both trending up  => aligned (True)
        """
        tfs = (self.config.timeframe,) + self.config.higher_timeframes
        signs: List[int] = []

        for tf in tfs:
            feats = ctx.get_feature_snapshot(symbol, tf) or {}
            trend = float(feats.get("trend_strength", feats.get("ema_slope", 0.0)))
            if trend > 0:
                signs.append(1)
            elif trend < 0:
                signs.append(-1)
            else:
                signs.append(0)

        non_zero = [s for s in signs if s != 0]
        if not non_zero:
            return False

        pos = sum(1 for s in non_zero if s > 0)
        neg = sum(1 for s in non_zero if s < 0)
        return pos == len(non_zero) or neg == len(non_zero)

    def _regime_onehot(self, regime: str) -> List[float]:
        regime = regime.lower()
        return [
            1.0 if regime == "trend" else 0.0,
            1.0 if regime in ("meanrev", "mean_reversion") else 0.0,
            1.0 if regime in ("chop", "range", "sideways") else 0.0,
        ]


# =====================================================================
#  ISE STRATEGY
# =====================================================================
class ISEProbabilityStrategy(StrategyBase):
    """
    ISE "80%+ win rate mode" hybrid strategy.

    - Uses ISEProbabilityEngine to compute per-trade win probability.
    - Applies VWAP / anchored VWAP / MTFA / OB/FVG / L2 filters.
    - Emits StrategySignal objects with embedded probability + meta,
      including SL/TP/trailing hints at the ATR level.
    """

    def __init__(
        self,
        ise_config: Optional[ISEProbabilityConfig] = None,
        engine: Optional[ISEProbabilityEngine] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Typical usage in tests:

            cfg = ISEProbabilityConfig(...)
            engine = ISEProbabilityEngine(cfg, ml_model=None)
            strat = ISEProbabilityStrategy(cfg, engine)

        Also supports:
            ISEProbabilityStrategy(ise_config=None, engine=None, config={...})
        """
        # Resolve ISE config:
        if ise_config is None:
            if isinstance(config, dict):
                base = ISEProbabilityConfig().__dict__.copy()
                base.update(config)
                ise_config = ISEProbabilityConfig(**base)
            else:
                ise_config = ISEProbabilityConfig()

        cfg_dict = ise_config.__dict__.copy()
        super().__init__(config=cfg_dict)

        self.ise_config = ise_config
        self.engine = engine or ISEProbabilityEngine(self.ise_config, ml_model=None)

    def generate_signals(
        self,
        ctx: ContextProtocol,
        screening_results: Dict[str, List[ScreeningResult]],
    ) -> List[StrategySignal]:
        if not self.ise_config.enabled:
            return []

        wl_syms = set(ctx.watchlist(self.ise_config.watchlist_name))
        if not wl_syms:
            return []

        # Collect candidates from screening results
        all_results: List[ScreeningResult] = [
            r for lst in screening_results.values() for r in lst
        ]
        candidates = [r for r in all_results if r.symbol in wl_syms]

        # Sort by screen score descending
        candidates.sort(key=lambda r: r.score, reverse=True)

        signals: List[StrategySignal] = []

        for r in candidates:
            if len(signals) >= self.ise_config.max_positions:
                break

            fv = self.engine.build_features(ctx, r.symbol)
            if fv is None:
                continue

            win_prob = self.engine.predict_win_prob(fv)

            # High-confidence filter (80%+ mode lives here)
            if win_prob < self.ise_config.min_win_prob:
                continue

            side = "BUY" if r.score >= 0 else "SELL"

            # If VWAP bias is enabled, ensure alignment
            bias = fv.meta.get("vwap_bias", 0.0)
            if self.ise_config.use_vwap_bias:
                if side == "BUY" and bias < 0:
                    continue
                if side == "SELL" and bias > 0:
                    continue

            # Size via ATR inverse, capped by max_per_symbol
            atr = float(fv.meta.get("atr", 1.0))
            inv_vol = 1.0 / max(atr, 1e-6)
            raw_size = min(self.ise_config.max_per_symbol, inv_vol)

            if raw_size <= 0.0:
                continue

            # ----------------------------------------------------------
            # SL / TP / Trailing hints (purely meta; router uses them)
            # ----------------------------------------------------------
            sl_dist_atr = atr * self.ise_config.sl_atr_mult
            tp_dist_atr = atr * self.ise_config.tp_atr_mult

            trailing_cfg = {
                "breakeven_after_r": self.ise_config.breakeven_after_r,
                "trail_after_r": self.ise_config.trail_after_r,
                "trail_atr_mult": self.ise_config.trail_atr_mult,
            }

            signals.append(
                StrategySignal(
                    strategy=self.ise_config.name,
                    symbol=r.symbol,
                    side=side,
                    size=raw_size,
                    meta={
                        "win_prob": win_prob,
                        "screen_score": r.score,
                        "regime": fv.meta.get("regime"),
                        "atr": atr,
                        "features": fv.meta,
                        # SL / TP / trailing hints in ATR-space:
                        "sl_atr_mult": self.ise_config.sl_atr_mult,
                        "tp_atr_mult": self.ise_config.tp_atr_mult,
                        "sl_dist_atr": sl_dist_atr,
                        "tp_dist_atr": tp_dist_atr,
                        "trailing": trailing_cfg,
                    },
                )
            )

        return signals
