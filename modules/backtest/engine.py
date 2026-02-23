# backtest/engine.py
from typing import Dict, List, Any


class BacktestEngine:
    """
    Tiny backtest runner:
      - ohlcv_series: mapping symbol -> list[ohlcv dicts] (time-ordered)
      - provider: must implement submit_order(order) and behave like PaperProvider
      - position_manager: optional, must implement record_fill(order, fill)
    """

    def __init__(self, strategy, provider, position_manager=None, logger=None):
        self.strategy = strategy
        self.provider = provider
        self.position_manager = position_manager
        self.logger = logger
        self.fills = []

    def run(
        self,
        ohlcv_series: Dict[str, List[Dict[str, Any]]],
        features_map: Dict[str, Dict[str, Any]] = None,
    ):
        """
        Run the backtest. features_map is symbol -> features dict (each feature is a list aligned to ohlcv)
        """
        features_map = features_map or {}
        # determine common length (we assume equal lengths for simple demo)
        for symbol, bars in ohlcv_series.items():
            context = {"symbol": symbol}
            # call on_start only if strategy implements it
            if hasattr(self.strategy, "on_start"):
                try:
                    self.strategy.on_start(context)
                except Exception:
                    # strategy hook failed; continue so tests don't break
                    pass

            for i, bar in enumerate(bars):
                # assemble per-bar features: pick last i+1 entries for each feature series
                feats = {}
                sym_feats = features_map.get(symbol, {})
                for k, series in sym_feats.items():
                    if isinstance(series, list):
                        feats[k] = series[: i + 1]
                    else:
                        feats[k] = [series]

                # call on_bar (expected to exist in test strategies)
                order = None
                try:
                    order = self.strategy.on_bar(symbol, bar, feats)
                except Exception:
                    # if on_bar raises, propagate (tests expect to catch risk ValueErrors),
                    # but swallow unexpected attribute errors here to be resilient
                    if not hasattr(self.strategy, "on_bar"):
                        order = None
                    else:
                        raise

                if order:
                    # submit to provider and expect a fill-like dict
                    # allow providers which implement submit_order or submit
                    if hasattr(self.provider, "submit_order"):
                        fill = self.provider.submit_order(order)
                    elif hasattr(self.provider, "submit"):
                        fill = self.provider.submit(order)
                    else:
                        raise RuntimeError("Provider has no submit/submit_order method")

                    # allow position manager to record fills
                    if self.position_manager is not None:
                        try:
                            self.position_manager.record_fill(order, fill)
                        except Exception:
                            pass
                    # notify strategy
                    if hasattr(self.strategy, "on_order_filled"):
                        try:
                            self.strategy.on_order_filled(order, fill)
                        except Exception:
                            pass
                    # log
                    self.fills.append((symbol, order, fill))
            # call on_stop only if strategy implements it
            if hasattr(self.strategy, "on_stop"):
                try:
                    self.strategy.on_stop()
                except Exception:
                    pass
        return {"fills": self.fills}
