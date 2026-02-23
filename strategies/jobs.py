from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from strategies.base import StrategyBase


class StrategyJob:
    """
    Orchestrates:

        watchlist -> (bar, features) -> strategy.on_bar -> router.submit

    Supercharged:
      - Passes a context into strategy.on_start with:
            feature_store, ohlcv_store, watchlists, router, extra
      - Strategy remains pure (no I/O), job handles integration.

    Hybrid:
      - Works in live (real stores/router) and tests (fake stores/router).

    Dynamic:
      - Driven by a small config (watchlist/timeframe/max_symbols).
    """

    def __init__(
        self,
        strategy: StrategyBase,
        router: Any,
        watchlists: Any,
        feature_store: Any,
        ohlcv_store: Any,
        config: Optional[Dict[str, Any]] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.strategy = strategy
        self.router = router
        self.watchlists = watchlists
        self.feature_store = feature_store
        self.ohlcv_store = ohlcv_store
        self.config: Dict[str, Any] = {
            "watchlist_name": "DAY_SCALP",
            "timeframe": "1m",
            "max_symbols": 100,
        }
        if config:
            self.config.update(config)
        self.extra_context = dict(extra_context or {})

    # --------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------
    def run_once(
        self,
        watchlist_name: Optional[str] = None,
        timeframe: Optional[str] = None,
        symbols: Optional[Iterable[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Run one iteration of the strategy job.

        Parameters
        ----------
        watchlist_name:
            Name of the watchlist from which to pull symbols.
            Defaults to config["watchlist_name"].

        timeframe:
            Timeframe used when querying bars/features.
            Defaults to config["timeframe"].

        symbols:
            Optional explicit symbol list. If provided, it overrides the
            watchlist symbols.

        Returns
        -------
        List[Dict[str, Any]]:
            List of order dicts that were actually submitted to the router.
        """
        wl_name = watchlist_name or self.config["watchlist_name"]
        tf = timeframe or self.config["timeframe"]

        if symbols is not None:
            symbol_list = list(symbols)
        else:
            # watchlists.get(name) -> list of symbols
            symbol_list = list(self.watchlists.get(wl_name) or [])

        max_symbols = int(self.config.get("max_symbols", len(symbol_list)))
        symbol_list = symbol_list[:max_symbols]

        # Build and pass context to strategy
        ctx = {
            "feature_store": self.feature_store,
            "ohlcv_store": self.ohlcv_store,
            "watchlists": self.watchlists,
            "router": self.router,
        }
        ctx.update(self.extra_context)

        self.strategy.on_start(ctx)

        submitted_orders: List[Dict[str, Any]] = []

        for sym in symbol_list:
            bar = self._get_latest_bar(sym, tf)
            if bar is None:
                continue
            features = self._get_latest_features(sym, tf)
            order = self.strategy.on_bar(sym, bar, features)
            if order:
                # job is responsible for calling router
                self.router.submit(order)
                submitted_orders.append(order)

        self.strategy.on_stop()
        return submitted_orders

    # --------------------------------------------------------------
    # Internal helpers: best-effort bar & feature access
    # --------------------------------------------------------------
    def _get_latest_bar(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        ohlcv = self.ohlcv_store
        # Try common method names
        for attr in ("latest_bar", "get_latest_bar", "last_bar"):
            fn = getattr(ohlcv, attr, None)
            if callable(fn):
                try:
                    bar = fn(symbol, timeframe)
                    return bar
                except TypeError:
                    # maybe the function only takes symbol
                    try:
                        bar = fn(symbol)
                        return bar
                    except Exception:
                        continue
                except Exception:
                    continue
        # As a last resort, allow the store itself to be a dict-like mapping
        try:
            maybe = ohlcv[symbol]
            if isinstance(maybe, dict):
                return maybe
        except Exception:
            pass
        return None

    def _get_latest_features(
        self,
        symbol: str,
        timeframe: str,
    ) -> Dict[str, Any]:
        fs = self.feature_store

        # Try a direct latest(symbol, timeframe) style API
        for attr in ("latest", "get_latest", "latest_feature", "get_feature"):
            fn = getattr(fs, attr, None)
            if callable(fn):
                try:
                    fv = fn(symbol, timeframe)
                    if isinstance(fv, dict):
                        return fv
                    # Some stores may return an object with .values
                    values = getattr(fv, "values", None)
                    if isinstance(values, dict):
                        return dict(values)
                except TypeError:
                    # maybe only symbol is required
                    try:
                        fv = fn(symbol)
                        if isinstance(fv, dict):
                            return fv
                        values = getattr(fv, "values", None)
                        if isinstance(values, dict):
                            return dict(values)
                    except Exception:
                        continue
                except Exception:
                    continue

        # Try snapshot() based API: snapshot()[symbol][timeframe]
        snap = getattr(fs, "snapshot", None)
        if callable(snap):
            try:
                s = snap()
                # Many implementations snapshot as {symbol: {timeframe: features_dict}}
                maybe = s.get(symbol, {}).get(timeframe)
                if isinstance(maybe, dict):
                    return maybe
            except Exception:
                pass

        # Fallback: empty feature dict
        return {}
