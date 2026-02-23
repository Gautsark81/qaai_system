# modules/strategy/orchestrator.py
"""
StrategyOrchestrator

Coordinates multiple strategy instances, optional meta-model scoring, and
order routing. Designed for non-invasive integration with your existing
Strategy objects (StrategyFactory, StreamRuleAdapter, etc.), MetaModel,
and OrderRouter.

Usage example:
    from modules.strategy.orchestrator import StrategyOrchestrator
    so = StrategyOrchestrator(
        strategies={"rules": my_rule_strategy, "momentum": my_ml_strategy},
        meta_model=maybe_meta_model,
        order_router=maybe_order_router,
        cfg={"aggregation": "priority", "model_thresholds": {...}}
    )
    so.prepare(historical_df)
    so.run_once(latest_feature_df_row)  # will evaluate and (optionally) send orders
"""

from __future__ import annotations
import logging
from typing import Dict, Any, Optional, Callable, List, Iterable, Tuple
import pandas as pd
import numpy as np
import time

logger = logging.getLogger(__name__)

# Optional imports — these modules may or may not exist in every workspace.
try:
    from modules.meta.model import MetaModel
except Exception:
    MetaModel = None  # type: ignore

try:
    from modules.execution.order_router import OrderRouter
except Exception:
    OrderRouter = None  # type: ignore

try:
    from modules.observability.metrics import Metrics
    _metrics = Metrics()
except Exception:
    _metrics = None


class StrategyOrchestrator:
    """
    Orchestrates multiple strategies and an optional meta-model and order router.

    Parameters
    ----------
    strategies : Dict[str, Any]
        Mapping of strategy name -> strategy instance. Strategy must implement:
            - prepare(historical_features: Iterable[Dict]) -> None
            - generate_signals(df: pd.DataFrame) -> pd.DataFrame (with 'signal' column)
      The df passed into generate_signals may contain multiple columns; strategy decides which to use.
    meta_model : Optional[MetaModel]
        Optional meta-model instance (modules.meta.model.MetaModel) to score vectors.
    order_router : Optional[OrderRouter]
        Optional order router to submit orders idempotently.
    cfg : dict
        Orchestrator-level config. Recognized keys:
          - aggregation: "priority" (default) | "weighted" | "sum_clip"
          - strategy_weights: {name: float} used only for "weighted" aggregation
          - model_thresholds: {"min_p_buy": 0.6, "max_p_sell": 0.6}
          - feature_cols: list[str] columns to use for meta-model prediction
          - order_defaults: {"size": 1.0}
          - dry_run: bool (if True, do not send orders)
    """

    def __init__(
        self,
        strategies: Dict[str, Any],
        meta_model: Optional[MetaModel] = None,
        order_router: Optional[OrderRouter] = None,
        cfg: Optional[Dict[str, Any]] = None,
    ):
        self.strategies = strategies or {}
        self.meta_model = meta_model
        self.order_router = order_router
        self.cfg = cfg or {}
        self.aggregation = self.cfg.get("aggregation", "priority")
        self.strategy_weights = self.cfg.get("strategy_weights", {})
        self.model_thresholds = self.cfg.get("model_thresholds", {})
        self.feature_cols = self.cfg.get("feature_cols", None)
        self.order_defaults = self.cfg.get("order_defaults", {"size": 1.0})
        self.dry_run = bool(self.cfg.get("dry_run", False))

        # internal state
        self._prepared = False
        self._last_run_metrics: Dict[str, Any] = {}

    # ------------------------
    # Preparation
    # ------------------------
    def prepare(self, historical_features: Iterable[Dict[str, Any]]) -> None:
        """
        Prepare each strategy with historical features (list of dicts or DataFrame rows).
        Strategies expecting DataFrames should handle converting the iterable.
        """
        for name, strat in self.strategies.items():
            try:
                if hasattr(strat, "prepare"):
                    strat.prepare(historical_features)
                    logger.debug("Prepared strategy %s", name)
            except Exception:
                logger.exception("Failed to prepare strategy %s", name)
        self._prepared = True

    # ------------------------
    # Run / Evaluate
    # ------------------------
    def run_once(self, fused_df: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluate all strategies on fused_df and produce a combined result DataFrame.

        Args:
            fused_df: DataFrame with features (one or more rows). We evaluate row-wise.

        Returns:
            result_df: DataFrame with combined columns:
               - per-strategy signal columns: <strategy>.signal
               - per-strategy priority columns if present: <strategy>.priority
               - p_buy/p_sell/p_hold (if meta_model present)
               - aggregated 'signal' column (int in -1,0,1)
               - optionally 'order' column with order payload dict (if order_router used)
        """
        if not isinstance(fused_df, pd.DataFrame):
            raise ValueError("fused_df must be a pandas DataFrame")

        # copy input to avoid in-place changes
        df = fused_df.copy().reset_index(drop=True)

        # 1) Optionally add meta-model probabilities first (so rules/strategies can use)
        if self.meta_model is not None and self.feature_cols:
            try:
                probs = self._predict_meta_probs(df)
                # probs is a DataFrame or dict-like; merge into df
                if isinstance(probs, pd.DataFrame):
                    for c in probs.columns:
                        df[c] = probs[c].values
                elif isinstance(probs, dict):
                    for k, v in probs.items():
                        df[k] = v
                else:
                    # handle list-of-dicts
                    pdf = pd.DataFrame(probs)
                    for c in pdf.columns:
                        df[c] = pdf[c].values
                logger.debug("Meta-model probabilities added to dataframe")
            except Exception:
                logger.exception("Meta-model prediction failed; continuing without probs")

        # 2) Collect individual strategy outputs
        strat_results: Dict[str, pd.DataFrame] = {}
        for name, strat in self.strategies.items():
            try:
                # strategy.generate_signals should return a DataFrame with 'signal' column
                out = strat.generate_signals(df.copy())
                # normalize signal column type
                if "signal" not in out.columns:
                    # If strategy returned bool mask or series, attempt to coerce
                    if hasattr(out, "to_frame"):
                        out = out.to_frame(name="signal")
                    else:
                        out["signal"] = 0
                # ensure -1/0/1 and int8
                out["signal"] = out["signal"].astype(int).clip(-1, 1).astype("int8")
                # rename signal column to include strategy prefix to avoid collisions
                sig_col = f"{name}.signal"
                out = out.rename(columns={"signal": sig_col})
                strat_results[name] = out[[sig_col]].reset_index(drop=True)
                # also optionally expose priority if available in strategy output
                # (some strategies may emit "<name>.priority")
                prio_col = f"{name}.priority"
                if prio_col in out.columns:
                    strat_results[name][prio_col] = out[prio_col]
                logger.debug("Strategy %s produced signals", name)
            except Exception:
                logger.exception("Strategy %s failed during generate_signals", name)
                # produce zero signals so aggregation continues
                n = len(df)
                strat_results[name] = pd.DataFrame({f"{name}.signal": [0] * n})

        # 3) Join all strategy signal columns into a single DataFrame aligned with df
        for name, subdf in strat_results.items():
            # ensure alignment
            df = pd.concat([df.reset_index(drop=True), subdf.reset_index(drop=True)], axis=1)

        # 4) Aggregate across strategies according to aggregation mode
        df["aggregated_signal"] = self._aggregate_signals(df, list(self.strategies.keys()))

        # 5) Optionally apply model thresholds to filter or modify aggregated_signal
        df["final_signal"] = df["aggregated_signal"].copy()
        if self.meta_model is not None and self.model_thresholds:
            df["final_signal"] = df.apply(self._apply_model_thresholds_row, axis=1)

        # 6) Optionally produce orders from final_signal and route them
        orders = []
        df["order"] = None
        if not self.dry_run and self.order_router is not None:
            for idx, row in df.iterrows():
                s = int(row["final_signal"])
                if s == 0:
                    continue
                order = self._build_order_from_row(row, signal=s)
                try:
                    resp = self.order_router.send(order)
                    row_order = {"order": order, "response": resp}
                    df.at[idx, "order"] = row_order
                    orders.append(row_order)
                    if _metrics:
                        _metrics.inc_order(1)
                    logger.info("Order routed: %s", order)
                except Exception:
                    if _metrics:
                        _metrics.inc_order_error(1)
                    logger.exception("Order routing failed for %s", order)

        # record last-run metrics
        self._last_run_metrics = {
            "n_rows": len(df),
            "n_orders": len(orders),
            "timestamp": time.time(),
        }

        return df

    # ------------------------
    # Helpers
    # ------------------------
    def _predict_meta_probs(self, df: pd.DataFrame):
        """
        Call meta_model.predict_proba with feature columns.
        Returns a DataFrame or list/dict as provided by MetaModel.
        """
        if self.meta_model is None:
            raise RuntimeError("No meta_model configured")

        cols = self.feature_cols
        if cols is None:
            raise ValueError("feature_cols must be configured to predict meta-model probabilities")

        X = df[cols].to_numpy()
        try:
            out = self.meta_model.predict_proba(X)
            # model may return dict for single sample, list of dicts for many, or pandas-friendly arrays
            # normalize into DataFrame if possible
            if isinstance(out, dict):
                # single-sample dict -> return dict (will be broadcast)
                return out
            if isinstance(out, list):
                return pd.DataFrame(out)
            # fallback: try to convert to ndarray
            return pd.DataFrame(out)
        except Exception:
            logger.exception("meta_model.predict_proba failed")
            raise

    def _aggregate_signals(self, df: pd.DataFrame, strategy_names: List[str]) -> pd.Series:
        """
        Aggregate columns "<name>.signal" according to selected aggregation.
        Supported: "priority" (default), "weighted", "sum_clip".
        - priority: per-row, strategy with highest absolute signal (or configured priority weights) wins.
        - weighted: sum(strategy_signal * strategy_weight) then clip.
        - sum_clip: legacy sum then clip.
        """
        n = len(df)
        out = pd.Series([0] * n, index=df.index, dtype="int8")

        sig_cols = [f"{name}.signal" for name in strategy_names if f"{name}.signal" in df.columns]
        if not sig_cols:
            return out

        if self.aggregation == "sum_clip":
            s = df[sig_cols].sum(axis=1)
            return s.clip(-1, 1).astype("int8")

        if self.aggregation == "weighted":
            weights = [float(self.strategy_weights.get(name, 1.0)) for name in strategy_names]
            # align weights with columns
            aligned_weights = []
            for name in strategy_names:
                col = f"{name}.signal"
                if col in df.columns:
                    aligned_weights.append(float(self.strategy_weights.get(name, 1.0)))
            vals = df[sig_cols].to_numpy(dtype=int)
            weighted = (vals * np.array(aligned_weights)).sum(axis=1)
            return pd.Series(np.clip(weighted, -1, 1).astype(int), index=df.index).astype("int8")

        # default: priority across strategies
        # Strategy-level priority: higher absolute signal magnitude wins; we can use provided weights as tie-breaker.
        priorities = {name: float(self.strategy_weights.get(name, 0.0)) for name in strategy_names}
        # compute per-row selection
        selected = []
        for idx in df.index:
            best_score = 0
            best_sum = 0
            for name in strategy_names:
                col = f"{name}.signal"
                if col not in df.columns:
                    continue
                val = int(df.at[idx, col])
                absval = abs(val)
                # primary: abs(val) (1 wins over 0)
                # secondary: strategy weight (higher preferred)
                prio = priorities.get(name, 0.0)
                key = (absval, prio)
                if key > (best_score, 0):
                    best_score = absval
                    best_sum = val
                elif key == (best_score, prio):
                    # tie on abs & prio -> sum
                    best_sum += val
            # clip to [-1,1]
            sel = int(max(min(best_sum, 1), -1))
            selected.append(sel)
        return pd.Series(selected, index=df.index, dtype="int8")

    def _apply_model_thresholds_row(self, row: pd.Series) -> int:
        """
        Using p_buy / p_sell from model, optionally override or mute signals.
        Example policy:
          - if signal == 1 and p_buy < min_p_buy -> downgrade to 0
          - if signal == -1 and p_sell < min_p_sell -> downgrade to 0
        """
        s = int(row["aggregated_signal"])
        if s == 0:
            return 0
        p_buy = float(row.get("p_buy", 0.0))
        p_sell = float(row.get("p_sell", 0.0))
        min_p_buy = float(self.model_thresholds.get("min_p_buy", 0.0))
        min_p_sell = float(self.model_thresholds.get("min_p_sell", 0.0))
        # if thresholds not configured, keep signal
        if s > 0:
            if min_p_buy > 0 and p_buy < min_p_buy:
                return 0
            return 1
        else:
            if min_p_sell > 0 and p_sell < min_p_sell:
                return 0
            return -1

    def _build_order_from_row(self, row: pd.Series, signal: int) -> Dict[str, Any]:
        """
        Build an order payload dict from a row and a signal.
        Minimal fields: symbol, side, size, client_tag (protection hash will add client_tag if missing).
        """
        sym = row.get("symbol") or row.get("s") or row.get("instrument")
        size = float(row.get("size", self.order_defaults.get("size", 1.0)))
        side = "BUY" if signal > 0 else "SELL"
        # embed some meta for traceability
        order = {
            "symbol": sym,
            "side": side,
            "size": size,
            "price": row.get("price"),  # optional market/limit handling left to order router
            "meta": {
                "src": "orchestrator",
                "strategy_snapshot": {k: row.get(k) for k in row.index if isinstance(k, str) and (".signal" in k or k in ["p_buy", "p_sell"])},
            }
        }
        # Add client_tag if present in row, allow router to compute protection hash otherwise
        if "client_tag" in row:
            order["client_tag"] = row["client_tag"]
        return order

    # ------------------------
    # Introspection / Helpers
    # ------------------------
    def last_run_metrics(self) -> Dict[str, Any]:
        return self._last_run_metrics

    def add_strategy(self, name: str, strat: Any) -> None:
        self.strategies[name] = strat

    def remove_strategy(self, name: str) -> None:
        if name in self.strategies:
            self.strategies.pop(name)
