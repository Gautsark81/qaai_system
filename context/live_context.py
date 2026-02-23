# File: qaai_system/context/live_context.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Protocol

from infra.logging import get_logger
from qaai_system.data.ohlcv_store import OHLCVStore, OHLCVBar
from qaai_system.data.feature_store import FeatureStore

logger = get_logger("context.live_context")


# ----------------------------------------------------------------------
# Optional type protocol (for ISE & IDEs only)
# ----------------------------------------------------------------------
class L2Provider(Protocol):
    """
    Minimal protocol for an order-book / L2 provider.

    Implementations may expose:
      - snapshot(symbol) -> dict
      - get_book(symbol) -> dict
      - get_l2(symbol)   -> dict

    LiveContext will try these in order.
    """

    def snapshot(self, symbol: str) -> Dict[str, Any]: ...
    # other methods optional / duck-typed


class VWAPProvider(Protocol):
    """
    Optional dedicated VWAP provider (e.g. per-session VWAP calculator).

    Implementations may expose:
      - get_vwap(symbol, timeframe) -> float
      - anchored_vwap(symbol, anchor_id) -> float
    """

    def get_vwap(self, symbol: str, timeframe: str) -> float: ...
    def anchored_vwap(self, symbol: str, anchor_id: str) -> float: ...


@dataclass
class LiveContext:
    """
    Live runtime context for strategies (ISE, MomentumVNext, etc).

    This is the thin “glue” that satisfies ISE's ContextProtocol:

        - watchlist(name) -> List[str]
        - get_feature_snapshot(symbol, timeframe) -> Dict[str, Any]
        - get_l2_snapshot(symbol) -> Dict[str, Any]
        - get_vwap(symbol, timeframe) -> float
        - get_anchored_vwap(symbol, anchor_id) -> float

    and provides a few extra conveniences:

        - get_last_price(symbol, timeframe="1m") -> float
        - log_meta(event, payload) -> None
    """

    ohlcv_store: OHLCVStore
    feature_store: FeatureStore

    # watchlists: name -> list of symbols
    watchlists: Mapping[str, List[str]] = field(default_factory=dict)

    # optional providers
    l2_provider: Optional[L2Provider] = None
    vwap_provider: Optional[VWAPProvider] = None

    default_timeframe: str = "1m"

    # ------------------------------------------------------------------
    # Watchlists
    # ------------------------------------------------------------------
    def watchlist(self, name: str) -> List[str]:
        """
        Return the current symbol list for a named watchlist.

        ISE expects "DAY_SCALP" or similar; this call is intentionally
        lenient: unknown lists simply return [].
        """
        try:
            syms = self.watchlists.get(name, [])
            return list(syms) if syms else []
        except Exception:
            logger.exception("watchlist lookup failed for %s", name)
            return []

    # ------------------------------------------------------------------
    # Features
    # ------------------------------------------------------------------
    def get_feature_snapshot(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Strategy-level feature snapshot for (symbol, timeframe).

        Resolution order:
          1) Flat snapshot store: FeatureStore.load_features()
          2) Streaming latest point: FeatureStore.latest().values + regime
        """
        try:
            # 1) preferred: persisted logical snapshot (used by your drift stack)
            snap = self.feature_store.load_features(symbol, timeframe)
            if snap is not None:
                return dict(snap)

            # 2) fallback: streaming history's latest point
            latest = self.feature_store.latest(symbol, timeframe)
            if latest is None:
                return {}

            feat = dict(latest.values)
            if latest.regime is not None:
                # normalise field name to what ISE config expects
                feat.setdefault("regime", latest.regime)
            # carry meta if present
            if latest.meta:
                # don't overwrite numeric features
                for k, v in latest.meta.items():
                    feat.setdefault(k, v)
            return feat
        except Exception:
            logger.exception(
                "get_feature_snapshot failed for %s/%s", symbol, timeframe
            )
            return {}

    # ------------------------------------------------------------------
    # L2 / order book
    # ------------------------------------------------------------------
    def get_l2_snapshot(self, symbol: str) -> Dict[str, Any]:
        """
        Return latest L2 snapshot for a symbol.

        We try several common shapes on the configured l2_provider:
          - provider.snapshot(symbol)
          - provider.get_book(symbol)
          - provider.get_l2(symbol)

        If nothing works, returns {} so ISE falls back gracefully.
        """
        if self.l2_provider is None:
            return {}

        prov = self.l2_provider
        try:
            if hasattr(prov, "snapshot"):
                snap = prov.snapshot(symbol)  # type: ignore[attr-defined]
                if isinstance(snap, dict):
                    return snap
        except Exception:
            logger.debug("l2_provider.snapshot failed for %s", symbol, exc_info=True)

        for attr in ("get_book", "get_l2"):
            try:
                if hasattr(prov, attr):
                    fn = getattr(prov, attr)
                    snap = fn(symbol)
                    if isinstance(snap, dict):
                        return snap
            except Exception:
                logger.debug("l2_provider.%s failed for %s", attr, symbol, exc_info=True)

        return {}

    # ------------------------------------------------------------------
    # VWAP & anchored VWAP
    # ------------------------------------------------------------------
    def get_vwap(self, symbol: str, timeframe: str) -> float:
        """
        Return a VWAP-style price for (symbol, timeframe).

        Resolution order:
          1) Dedicated VWAPProvider.get_vwap (if configured)
          2) Back-of-envelope VWAP from OHLCV bars: sum(close * volume) / sum(volume)
          3) Fallback to last bar close (or 0.0 if unavailable)
        """
        # 1) dedicated provider
        if self.vwap_provider is not None:
            try:
                v = self.vwap_provider.get_vwap(symbol, timeframe)
                return float(v)
            except Exception:
                logger.debug(
                "vwap_provider.get_vwap failed for %s/%s",
                symbol,
                timeframe,
                exc_info=True,
            )

        # 2) approximate from OHLCV
        try:
            bars = self.ohlcv_store.get_bars(symbol, timeframe, limit=200)
        except Exception:
            bars = []

        if not bars:
            # 3) last-price fallback
            return float(self.get_last_price(symbol, timeframe) or 0.0)

        try:
            pv_sum = 0.0
            vol_sum = 0.0
            for b in bars:
                price = float(b.close)
                vol = float(b.volume)
                pv_sum += price * max(vol, 0.0)
                vol_sum += max(vol, 0.0)

            if vol_sum <= 0:
                return float(bars[-1].close)

            return pv_sum / vol_sum
        except Exception:
            logger.exception("VWAP computation failed for %s/%s", symbol, timeframe)
            return float(bars[-1].close)

    def get_anchored_vwap(self, symbol: str, anchor_id: str) -> float:
        """
        Anchored VWAP lookup for a liquidity sweep / OB anchor.

        Resolution order:
          1) Dedicated VWAPProvider.anchored_vwap(symbol, anchor_id)
          2) Feature snapshot key: `anchored_vwap_{anchor_id}`
          3) Fallback to standard VWAP
        """
        # 1) dedicated provider
        if self.vwap_provider is not None:
            try:
                v = self.vwap_provider.anchored_vwap(symbol, anchor_id)  # type: ignore[attr-defined]
                return float(v)
            except Exception:
                logger.debug(
                    "vwap_provider.anchored_vwap failed for %s/%s",
                    symbol,
                    anchor_id,
                    exc_info=True,
                )

        # 2) features-based anchored VWAP
        try:
            feats = self.get_feature_snapshot(symbol, self.default_timeframe)
            key = f"anchored_vwap_{anchor_id}"
            if key in feats:
                return float(feats[key])
        except Exception:
            logger.debug(
                "feature-based anchored_vwap lookup failed for %s/%s",
                symbol,
                anchor_id,
                exc_info=True,
            )

        # 3) fallback to normal VWAP
        return self.get_vwap(symbol, self.default_timeframe)

    # ------------------------------------------------------------------
    # Price helper
    # ------------------------------------------------------------------
    def get_last_price(self, symbol: str, timeframe: Optional[str] = None) -> float:
        """
        Last traded price approximation.

        Resolution order:
          1) Latest OHLCV bar close for timeframe (default '1m')
          2) Feature snapshot's last_price/close
          3) 0.0
        """
        tf = timeframe or self.default_timeframe

        # 1) OHLCV
        try:
            bar: Optional[OHLCVBar] = self.ohlcv_store.latest_bar(symbol, tf)
            if bar is not None:
                return float(bar.close)
        except Exception:
            logger.debug(
                "latest_bar lookup failed for %s/%s", symbol, tf, exc_info=True
            )

        # 2) feature snapshot
        try:
            feats = self.get_feature_snapshot(symbol, tf)
            if "last_price" in feats:
                return float(feats["last_price"])
            if "close" in feats:
                return float(feats["close"])
        except Exception:
            logger.debug(
                "feature-based last_price lookup failed for %s/%s",
                symbol,
                tf,
                exc_info=True,
            )

        return 0.0

    # ------------------------------------------------------------------
    # Logging / meta
    # ------------------------------------------------------------------
    def log_meta(self, event: str, payload: Dict[str, Any]) -> None:
        """
        Small helper used by MomentumVNext/ISE to log structured events.
        """
        try:
            logger.info({"evt": event, **(payload or {})})
        except Exception:
            logger.debug("log_meta failed for event=%s", event, exc_info=True)
