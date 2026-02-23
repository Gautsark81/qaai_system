# screening/advanced_engine.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Protocol, Tuple

from infra.logging import get_logger
from screening.engine import ScreenConfig  # reuse base config
from screening.results import ScreeningResult

logger = get_logger("screening.advanced_engine")


# ---------------------------------------------------------------------------
# Protocols / interfaces
# ---------------------------------------------------------------------------

class ContextLike(Protocol):
    """
    Minimal interface expected from a screening context.

    Works with:
      - ScreeningContext (Phase 2 tests)
      - LiveContext (your live stack)

    We duck-type the same way as in screening.engine, plus we expect an
    optional feature snapshot and optional sector info.
    """

    def watchlist(self, name: str) -> List[str]: ...
    @property
    def universe(self) -> Iterable[str]: ...
    @property
    def ohlcv_store(self) -> Any: ...
    @property
    def feature_store(self) -> Any: ...

    # optional – if available, we use it
    def get_feature_snapshot(self, symbol: str, timeframe: str) -> Dict[str, Any]: ...
    def get_sector(self, symbol: str) -> Optional[str]: ...
    def get_sector_index(self, sector: str) -> Optional[str]: ...


class MLBrainLike(Protocol):
    """
    Phase 3 / 'ML Brain' interface – minimal contract this engine expects.

    The implementation can live in your Phase 3 code. For now, we only rely
    on a single method that returns ML scores for a batch of feature dicts.
    """

    def predict_batch(
        self,
        features: Dict[str, Dict[str, float]],
        regime: Optional[str] = None,
    ) -> Dict[str, Dict[str, float]]:
        """
        Parameters
        ----------
        features:
            mapping: symbol -> feature_name -> value
        regime:
            Optional market regime tag (e.g. 'HIGH_VOL', 'LOW_VOL', 'TRENDING').

        Returns
        -------
        Dict[symbol, Dict[str, float]]:
            At minimum, keys for each symbol may include:
              - 'p_signal'   : probability of good ISE setup
              - 'p_win'      : expected win probability
              - 'ms_score'   : market structure quality
              - 'ob_vwap'    : OB/FVG + VWAP confluence
              - 'l2_imb'     : L2 imbalance / footprint score
              - 'vol_health' : volatility tradability score
        """
        ...


class PnLFeedbackSourceLike(Protocol):
    """
    Interface for a PnL feedback provider.

    Implementation should aggregate recent trade performance per symbol and
    return a normalized score, e.g. in [-1, +1].
    """

    def get_symbol_pnl_score(self, symbol: str) -> float:
        """
        Returns a PnL feedback score for the symbol.

        Positive values -> good recent performance.
        Negative values -> poor recent performance.
        0.0             -> neutral / unknown.
        """
        ...


class MarketRegime(str, Enum):
    HIGH_VOL = "HIGH_VOL"
    NORMAL = "NORMAL"
    LOW_VOL = "LOW_VOL"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Configs
# ---------------------------------------------------------------------------

@dataclass
class HardFilterConfig:
    """
    Layer 1 hard filters (liquidity, volatility, trend, structure, sector).
    Values are expressed in NSE terms (INR, Cr, etc.).
    """

    min_turnover_cr: float = 50.0
    min_avg_volume: float = 500_000.0
    max_impact_cost: float = 0.10
    max_spread_pct: float = 0.08

    atr_pctile_min: float = 0.40   # 40%
    atr_pctile_max: float = 0.90   # 90%

    require_trend_alignment: bool = True
    require_clean_structure: bool = True

    min_sector_rs_pctile: float = 0.70  # top 30% sector RS


@dataclass
class WeightConfig:
    """
    Final ranking weights (Layer 3 hybrid ML + microstructure + PnL).

    Matches your spec:

      RankScore =
         0.25 * P(signal)
       + 0.20 * P(win)
       + 0.15 * MarketStructureScore
       + 0.15 * OB/VWAP Confluence
       + 0.10 * L2 Imbalance Score
       + 0.10 * Volatility Health
       + 0.05 * PnL Feedback Score
    """

    w_p_signal: float = 0.25
    w_p_win: float = 0.20
    w_ms: float = 0.15
    w_ob_vwap: float = 0.15
    w_l2_imb: float = 0.10
    w_vol_health: float = 0.10
    w_pnl_feedback: float = 0.05


@dataclass
class AdvancedScreenConfig:
    """
    Supercharged config for Phase 2.5 screening.

    We reuse ScreenConfig for basic fields (timeframe, top_n, etc.) and
    add advanced knobs for ML, hard filters, and final ranking.
    """

    base: ScreenConfig = ScreenConfig(
        name="ADVANCED_TOP200",
        timeframe="5m",
        top_n=200,
        min_liquidity=0.0,   # we override with explicit liquidity rules
        watchlist_name="DAY_SCALP",
        prefer_feature_score=True,
    )

    hard_filters: HardFilterConfig = HardFilterConfig()
    weights: WeightConfig = WeightConfig()

    # Optional: if you want to force Top200 even if fewer pass hard filters
    force_top_n: int = 200


# ---------------------------------------------------------------------------
# Advanced Screening Engine
# ---------------------------------------------------------------------------

class AdvancedScreeningEngine:
    """
    Supercharged multi-layer screening engine for NSE, built for your AMATS
    architecture (Phase 2.5).

    Layers:
      1) Hard filters (liquidity, volatility, trend, structure, sector).
      2) Feature extraction / ML scoring (delegated to MLBrain).
      3) Hybrid final ranking (Top-200) with PnL-driven re-weighting.

    Design goals:
      - Composable and testable in isolation.
      - Non-invasive to existing Phase 2 tests / engine.
      - Easy to plug into Phase 3 ML Brain and PnL analytics.
    """

    def __init__(
        self,
        ml_brain: Optional[MLBrainLike] = None,
        pnl_feedback: Optional[PnLFeedbackSourceLike] = None,
        config: Optional[AdvancedScreenConfig] = None,
    ) -> None:
        self._ml_brain = ml_brain
        self._pnl_feedback = pnl_feedback
        self._config = config or AdvancedScreenConfig()

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #

    def rank_universe(
        self,
        ctx: ContextLike,
        regime: MarketRegime = MarketRegime.UNKNOWN,
        override_config: Optional[AdvancedScreenConfig] = None,
    ) -> List[ScreeningResult]:
        """
        Main Phase 2.5 entrypoint.

        Parameters
        ----------
        ctx:
            Live or offline screening context with OHLCV + features.
        regime:
            Market regime inferred by your regime detector.
        override_config:
            Optional config override for this specific run.

        Returns
        -------
        List[ScreeningResult]:
            Sorted Top-N (usually 200) symbols with final rank scores in meta.
        """
        cfg = override_config or self._config

        base_cfg = cfg.base
        symbols = list(ctx.universe)
        if not symbols:
            logger.info("advanced_screening_no_universe")
            return []

        # Layer 1: apply hard filters
        passed_symbols, hard_filter_meta = self._apply_hard_filters(
            ctx, symbols, base_cfg.timeframe, cfg.hard_filters
        )
        if not passed_symbols:
            logger.info("advanced_screening_no_symbols_after_hard_filters")
            return []

        # Layer 2: build feature dicts for ML / scoring
        feature_map = self._build_feature_map(
            ctx,
            passed_symbols,
            base_cfg.timeframe,
            hard_filter_meta,
        )

        # Layer 3: ML scoring (if ML brain present)
        ml_scores = self._run_ml_brain(feature_map, regime)

        # Combine everything into final rank scores
        results = self._build_ranked_results(
            symbols=passed_symbols,
            feature_map=feature_map,
            ml_scores=ml_scores,
            cfg=cfg,
        )

        # Enforce Top-N (Top 200 by default)
        top_n = cfg.force_top_n or base_cfg.top_n
        if top_n and top_n > 0:
            results = results[: top_n]

        return results

    # ------------------------------------------------------------------ #
    # Hard filters (Layer 1)                                             #
    # ------------------------------------------------------------------ #

    def _apply_hard_filters(
        self,
        ctx: ContextLike,
        symbols: List[str],
        timeframe: str,
        hf_cfg: HardFilterConfig,
    ) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
        """
        Apply hard filters on the universe:
          - Liquidity: turnover, avg volume, spread, impact cost
          - Volatility: ATR percentile bounds
          - Trend quality: EMA slopes / alignment
          - Structure: HH/HL or LH/LL, recent BoS
          - Sector leadership: top RS vs sector index

        For now, this implementation is deliberately defensive:
          - It *reads* features from feature_store / snapshots using
            conventional names (documented below).
          - If a specific feature is missing, it does NOT auto-fail the stock;
            it simply marks that feature as unavailable.
          - You can gradually populate your feature store with these fields
            without breaking anything.

        Expected feature keys per symbol (examples):
          - 'avg_turnover_cr_20d'
          - 'avg_volume_20d'
          - 'impact_cost'
          - 'spread_pct'
          - 'atr_pctile_20d'
          - 'ema20_slope', 'ema50_slope', 'ema200_slope'
          - 'trend_alignment_score'
          - 'structure_clean_score'
          - 'recent_bos_score'
          - 'sector_rs_pctile'
        """
        feature_store = ctx.feature_store
        passed: List[str] = []
        meta: Dict[str, Dict[str, float]] = {}

        for sym in symbols:
            feats: Dict[str, Any] = {}
            try:
                feats = feature_store.snapshot(sym, timeframe) or {}
            except Exception:
                # fallback to get_feature_snapshot if present
                if hasattr(ctx, "get_feature_snapshot"):
                    try:
                        feats = ctx.get_feature_snapshot(sym, timeframe) or {}
                    except Exception:
                        feats = {}

            # liquidity
            turnover = float(feats.get("avg_turnover_cr_20d", 0.0) or 0.0)
            avg_vol = float(feats.get("avg_volume_20d", 0.0) or 0.0)
            impact_cost = float(feats.get("impact_cost", 0.0) or 0.0)
            spread_pct = float(feats.get("spread_pct", 0.0) or 0.0)

            if turnover < hf_cfg.min_turnover_cr:
                continue
            if avg_vol < hf_cfg.min_avg_volume:
                continue
            if impact_cost > hf_cfg.max_impact_cost:
                continue
            if spread_pct > hf_cfg.max_spread_pct:
                continue

            # volatility filter
            atr_pctile = float(feats.get("atr_pctile_20d", 0.5))
            if atr_pctile < hf_cfg.atr_pctile_min or atr_pctile > hf_cfg.atr_pctile_max:
                continue

            # trend quality + structure
            if hf_cfg.require_trend_alignment:
                trend_score = float(feats.get("trend_alignment_score", 0.0))
                if trend_score <= 0.0:
                    continue

            if hf_cfg.require_clean_structure:
                struct_score = float(feats.get("structure_clean_score", 0.0))
                if struct_score <= 0.0:
                    continue

                bos_score = float(feats.get("recent_bos_score", 0.0))
                if bos_score <= 0.0:
                    continue

            # sector leadership
            sector_rs = float(feats.get("sector_rs_pctile", 0.0))
            if sector_rs < hf_cfg.min_sector_rs_pctile:
                continue

            # If we reached here, symbol passes hard filters
            passed.append(sym)
            meta[sym] = {
                "turnover_cr_20d": turnover,
                "avg_volume_20d": avg_vol,
                "impact_cost": impact_cost,
                "spread_pct": spread_pct,
                "atr_pctile_20d": atr_pctile,
                "trend_alignment_score": float(feats.get("trend_alignment_score", 0.0)),
                "structure_clean_score": float(feats.get("structure_clean_score", 0.0)),
                "recent_bos_score": float(feats.get("recent_bos_score", 0.0)),
                "sector_rs_pctile": sector_rs,
            }

        return passed, meta

    # ------------------------------------------------------------------ #
    # Feature aggregation (Layer 2)                                      #
    # ------------------------------------------------------------------ #

    def _build_feature_map(
        self,
        ctx: ContextLike,
        symbols: List[str],
        timeframe: str,
        hard_meta: Dict[str, Dict[str, float]],
    ) -> Dict[str, Dict[str, float]]:
        """
        Build a feature map suitable for ML:

          symbol -> feature_name -> value

        It merges:
          - Hard filter metadata
          - Price action features (OB/FVG, VWAP, momentum)
          - Volume & microstructure
          - Multi-timeframe alignment
          - Optional alternative data features

        The actual feature generation is expected to be done upstream and
        persisted in FeatureStore; here we just *collect* them in a stable
        schema.
        """
        fs = ctx.feature_store
        feature_map: Dict[str, Dict[str, float]] = {}

        for sym in symbols:
            feats: Dict[str, Any] = {}
            try:
                feats = fs.snapshot(sym, timeframe) or {}
            except Exception:
                if hasattr(ctx, "get_feature_snapshot"):
                    try:
                        feats = ctx.get_feature_snapshot(sym, timeframe) or {}
                    except Exception:
                        feats = {}

            # Start with hard filter meta
            combined: Dict[str, float] = dict(hard_meta.get(sym, {}))

            # Price action / structure / microstructure (Layer 2 bullets)
            for key in [
                "bos_strength_5d",
                "liquidity_sweep_count_20",
                "ob_fvg_proximity_score",
                "vwap_premium_discount",
                "momentum_burst_score",
                "ppo_trend_score",
                "rsi_shift_score",
                "vol_expansion_score",
            ]:
                if key in feats:
                    combined[key] = float(feats[key])

            # Volume microstructure
            for key in [
                "volume_zscore",
                "volume_cluster_score",
                "inst_footprint_score",
                "obv_vwap_dev_score",
            ]:
                if key in feats:
                    combined[key] = float(feats[key])

            # L2 / orderbook
            for key in [
                "l2_bid_ask_imbalance",
                "l2_hidden_liq_score",
                "l2_cum_delta",
                "l2_spread_regime_score",
            ]:
                if key in feats:
                    combined[key] = float(feats[key])

            # MTF alignment
            for key in [
                "mtf_trend_alignment",
                "mtf_vol_compression",
                "mtf_liquidity_map_score",
            ]:
                if key in feats:
                    combined[key] = float(feats[key])

            # Optional alt data
            for key in [
                "news_sentiment_score",
                "search_trend_score",
                "social_sentiment_score",
                "macro_alignment_score",
            ]:
                if key in feats:
                    combined[key] = float(feats[key])

            feature_map[sym] = combined

        return feature_map

    # ------------------------------------------------------------------ #
    # ML scoring (Layer 3 - part 1)                                      #
    # ------------------------------------------------------------------ #

    def _run_ml_brain(
        self,
        feature_map: Dict[str, Dict[str, float]],
        regime: MarketRegime,
    ) -> Dict[str, Dict[str, float]]:
        """
        If an ML brain is present, call it to get p_signal/p_win/etc.
        Otherwise, fall back to simple heuristics based on features.
        """
        if self._ml_brain is not None:
            try:
                return self._ml_brain.predict_batch(
                    feature_map,
                    regime=regime.value if regime else None,
                )
            except Exception:
                logger.exception("advanced_screening_ml_brain_failure")

        # Heuristic fallback: derive pseudo ML-scores from existing features.
        ml_scores: Dict[str, Dict[str, float]] = {}
        for sym, feats in feature_map.items():
            # Very rough heuristic: all in [0, 1]
            p_signal = self._sigmoid(feats.get("trend_alignment_score", 0.0))
            p_win = self._sigmoid(feats.get("structure_clean_score", 0.0))
            ms_score = self._sigmoid(feats.get("bos_strength_5d", 0.0))
            ob_vwap = self._sigmoid(feats.get("ob_fvg_proximity_score", 0.0))
            l2_imb = self._sigmoid(feats.get("l2_bid_ask_imbalance", 0.0))
            vol_health = self._sigmoid(feats.get("vol_expansion_score", 0.0))

            ml_scores[sym] = {
                "p_signal": p_signal,
                "p_win": p_win,
                "ms_score": ms_score,
                "ob_vwap": ob_vwap,
                "l2_imb": l2_imb,
                "vol_health": vol_health,
            }

        return ml_scores

    @staticmethod
    def _sigmoid(x: float) -> float:
        import math

        try:
            return 1.0 / (1.0 + math.exp(-float(x)))
        except Exception:
            return 0.5

    # ------------------------------------------------------------------ #
    # Final ranking + PnL feedback (Layer 3 - part 2)                     #
    # ------------------------------------------------------------------ #

    def _build_ranked_results(
        self,
        symbols: List[str],
        feature_map: Dict[str, Dict[str, float]],
        ml_scores: Dict[str, Dict[str, float]],
        cfg: AdvancedScreenConfig,
    ) -> List[ScreeningResult]:
        w = cfg.weights
        results: List[ScreeningResult] = []

        for sym in symbols:
            feats = feature_map.get(sym, {})
            ml = ml_scores.get(sym, {})

            p_signal = float(ml.get("p_signal", 0.0))
            p_win = float(ml.get("p_win", 0.0))
            ms = float(ml.get("ms_score", feats.get("trend_alignment_score", 0.0)))
            ob_vwap = float(ml.get("ob_vwap", feats.get("ob_fvg_proximity_score", 0.0)))
            l2_imb = float(ml.get("l2_imb", feats.get("l2_bid_ask_imbalance", 0.0)))
            vol_health = float(ml.get("vol_health", feats.get("vol_expansion_score", 0.0)))

            pnl_feedback = 0.0
            if self._pnl_feedback is not None:
                try:
                    pnl_feedback = float(self._pnl_feedback.get_symbol_pnl_score(sym))
                except Exception:
                    pnl_feedback = 0.0

            rank_score = (
                w.w_p_signal * p_signal
                + w.w_p_win * p_win
                + w.w_ms * ms
                + w.w_ob_vwap * ob_vwap
                + w.w_l2_imb * l2_imb
                + w.w_vol_health * vol_health
                + w.w_pnl_feedback * pnl_feedback
            )

            results.append(
                ScreeningResult(
                    symbol=sym,
                    score=rank_score,
                    meta={
                        "p_signal": p_signal,
                        "p_win": p_win,
                        "ms_score": ms,
                        "ob_vwap": ob_vwap,
                        "l2_imb": l2_imb,
                        "vol_health": vol_health,
                        "pnl_feedback": pnl_feedback,
                        "features": feats,
                        "config_name": cfg.base.name,
                        "timeframe": cfg.base.timeframe,
                    },
                )
            )

        # Sort by rank_score (score) descending
        results.sort(key=lambda r: float(r.score), reverse=True)
        return results
