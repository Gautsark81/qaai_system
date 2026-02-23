# qaai_system/watchlist_advanced.py
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional

from qaai_system.screener.supercharged_engine import ScreeningEngineSupercharged
from qaai_system.screener.meta_engine import MetaScreeningEngine


@dataclass
class WatchItem:
    symbol: str
    score: float
    weight: float
    vol: float
    reasons: Dict[str, float]


class AdvancedWatchlist:
    """
    Phase 4 polish:
      - Risk-aware sizing for suggested allocation weights
      - Explainability 'reason cards'
      - Adaptive refresh interval (based on volatility and signal churn)
    """

    def __init__(
        self,
        base_engine: Optional[ScreeningEngineSupercharged] = None,
        meta_engine: Optional[MetaScreeningEngine] = None,
        base_refresh_s: int = 15,
        min_refresh_s: int = 5,
        max_refresh_s: int = 60,
        vol_window: int = 20,
    ):
        self.engine = base_engine or ScreeningEngineSupercharged()
        self.meta = meta_engine
        self.base_refresh_s = int(base_refresh_s)
        self.min_refresh_s = int(min_refresh_s)
        self.max_refresh_s = int(max_refresh_s)
        self.vol_window = int(vol_window)
        self._last_top_symbols: List[str] = []

    # -------------------- Public API --------------------

    def build_watchlist(
        self,
        market_df: pd.DataFrame,
        top_k: int = 10,
        risk_budget: float = 1.0,
        per_symbol_cap: float = 0.2,
    ) -> List[WatchItem]:
        """
        Returns top_k WatchItems with risk-aware weights and reason cards.
        - risk_budget: total normalized budget (1.0 = 100%)
        - per_symbol_cap: maximum weight any single symbol can receive
        """
        candidates = market_df.copy()
        # Get base scores using the existing engine
        ranked = self.engine.screen(
            candidates, top_k=top_k * 3
        )  # more to allow post-filters
        # ranked is List[Tuple[symbol, score]]
        symbols = [s for s, _ in ranked]
        scores = {s: sc for s, sc in ranked}

        # Compute features we need for risk + reason cards
        feat = self._compute_min_features(
            candidates[candidates["symbol"].isin(symbols)]
        )

        # Select latest row per symbol
        latest = feat.groupby("symbol").tail(1).reset_index(drop=True)

        # Merge scores
        latest["score"] = latest["symbol"].map(scores).fillna(0.0)

        # Drop non-positive scores for sizing (keeps list clean)
        latest = latest[latest["score"] > 0].copy()
        if latest.empty:
            self._last_top_symbols = []
            return []

        # Rank by score and take top_k
        latest = (
            latest.sort_values("score", ascending=False)
            .head(top_k)
            .reset_index(drop=True)
        )

        # Risk-aware weights
        weights = self._suggest_weights(
            latest["score"].values,
            latest["vol"].values,
            risk_budget=risk_budget,
            cap=per_symbol_cap,
        )
        latest["weight"] = weights

        # Reason cards
        reasons = self._make_reason_cards(latest)

        items = [
            WatchItem(
                symbol=row["symbol"],
                score=float(row["score"]),
                weight=float(row["weight"]),
                vol=float(row["vol"]),
                reasons=reasons[row["symbol"]],
            )
            for _, row in latest.iterrows()
        ]

        # Save state for adaptive refresh
        self._last_top_symbols = [w.symbol for w in items]
        return items

    def next_refresh_seconds(
        self,
        market_df: pd.DataFrame,
        current_watchlist: List[WatchItem],
    ) -> int:
        """
        Adaptive refresh:
          - Higher realized volatility -> faster refresh
          - Higher signal churn (top list changed) -> faster refresh
        """
        if len(current_watchlist) == 0:
            # no items -> slower, but not too slow
            return max(self.base_refresh_s, self.min_refresh_s)

        # Mean vol across watchlist
        vol_mean = (
            float(np.nanmean([w.vol for w in current_watchlist]))
            if current_watchlist
            else 0.0
        )

        # Churn = Jaccard distance to last symbols
        new_syms = {w.symbol for w in current_watchlist}
        old_syms = set(self._last_top_symbols)
        if len(new_syms | old_syms) == 0:
            churn = 0.0
        else:
            jaccard = 1.0 - (
                len(new_syms & old_syms) / max(1, len(new_syms | old_syms))
            )
            churn = float(jaccard)

        # Map vol & churn to [0..1] via soft clipping
        v = np.tanh(vol_mean / 0.02)  # ~2% daily vol -> near 1.0
        c = np.tanh(churn / 0.5)

        # Blend into refresh factor: higher -> faster (smaller seconds)
        urgency = 0.6 * v + 0.4 * c  # weights can be tuned
        # Convert urgency to seconds between [min, max], inverted
        span = self.max_refresh_s - self.min_refresh_s
        secs = int(self.max_refresh_s - urgency * span)
        return int(np.clip(secs, self.min_refresh_s, self.max_refresh_s))

        # -------------------- Internals --------------------

    def _compute_min_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute minimal features needed for risk + reason cards:
            - returns, vol (rolling std)
            - momentum_10, momentum_20
            - volume_z
        """
        g = df.sort_values(["symbol", "timestamp"]).groupby(
            "symbol", group_keys=False, sort=False
        )

        def _feat(grp: pd.DataFrame) -> pd.DataFrame:
            px = grp["close"].astype(float)
            ret = px.pct_change().fillna(0.0)
            vol = ret.rolling(self.vol_window).std().bfill().fillna(ret.std() or 0.0)

            m10 = (px / px.shift(10) - 1.0).fillna(0.0)
            m20 = (px / px.shift(20) - 1.0).fillna(0.0)

            volu = grp["volume"].astype(float)
            vmean = volu.rolling(20).mean().bfill().fillna(volu.mean() or 0.0)
            vstd = (
                volu.rolling(20)
                .std()
                .bfill()
                .replace(0.0, np.nan)
                .fillna(volu.std() or 1.0)
            )
            vz = ((volu - vmean) / vstd).fillna(0.0)

            out = grp.copy()
            out["ret"] = ret
            out["vol"] = vol
            out["mom_10"] = m10
            out["mom_20"] = m20
            out["vol_z"] = vz
            return out

        # ✅ keep symbol column explicitly after apply
        result = g.apply(_feat, include_groups=False).reset_index(drop=True)
        if "symbol" not in result.columns and "symbol" in df.columns:
            result = result.merge(
                df[["symbol"]], left_index=True, right_index=True, how="left"
            )
        return result

    def _suggest_weights(
        self,
        scores: np.ndarray,
        vols: np.ndarray,
        risk_budget: float,
        cap: float,
    ) -> np.ndarray:
        """
        Risk-aware sizing:
          raw = score_pos * (1 / (1 + vol_norm))
          -> normalize to sum <= risk_budget
          -> apply per-symbol cap and renormalize if needed
        """
        scores = np.asarray(scores, dtype=float)
        vols = np.asarray(vols, dtype=float)

        s_pos = np.maximum(scores, 0.0)
        # Normalize vol roughly to [0..1] using 95th percentile
        v_ref = (
            np.nanpercentile(vols[~np.isnan(vols)], 95)
            if np.any(~np.isnan(vols))
            else 1e-6
        )
        v_norm = np.clip(vols / max(v_ref, 1e-6), 0.0, 5.0)

        raw = s_pos * (1.0 / (1.0 + v_norm))
        if np.all(raw <= 0):
            return np.zeros_like(raw)

        w = raw / raw.sum() * risk_budget
        # Apply caps
        w = np.minimum(w, cap)
        # If capped reduced total, we can optionally renormalize up to risk_budget (but keep caps)
        total = w.sum()
        if total > 0 and total < risk_budget:
            # Distribute remaining proportionally to uncapped headroom
            headroom = np.maximum(cap - w, 0.0)
            if headroom.sum() > 0:
                w += headroom * ((risk_budget - total) / headroom.sum())
        return w

    def _make_reason_cards(
        self, df_latest: pd.DataFrame
    ) -> Dict[str, Dict[str, float]]:
        """
        Build small explainability payloads per symbol.
        Keys:
          - momentum (blend of 10 & 20)
          - volume_pressure (vol_z)
          - volatility (vol)
          - rule_vs_ml (if meta engine present, expose weights)
        """
        out: Dict[str, Dict[str, float]] = {}
        for _, row in df_latest.iterrows():
            s = row["symbol"]
            momentum = 0.6 * float(row["mom_10"]) + 0.4 * float(row["mom_20"])
            volume_pressure = float(row["vol_z"])
            vol = float(row["vol"])
            card: Dict[str, float] = {
                "momentum": float(momentum),
                "volume_pressure": float(volume_pressure),
                "volatility": float(vol),
            }
            # If meta engine exists, expose current blend weights
            if hasattr(self.meta, "w_rule") and hasattr(self.meta, "w_ml"):
                card["w_rule"] = float(getattr(self.meta, "w_rule"))
                card["w_ml"] = float(getattr(self.meta, "w_ml"))
            out[s] = card
        return out
