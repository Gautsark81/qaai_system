from __future__ import annotations

from typing import Any, Dict, Optional, Mapping


class StrategyBase:
    """
    Minimal-but-production-grade base class for strategies.

    Design goals:
    - Keep full backward compatibility with existing code & tests.
    - Provide a clear, documented interface for live + backtest flows.
    - Add small utilities (config access, context management) so concrete
      strategies can stay clean and focused on trading logic.

    Lifecycle (backtest or live):

        s = MyStrategy(config)
        s.on_start(context)
        for bar in bars:
            maybe_order = s.on_bar(symbol, bar, features)
            ... route order if not None ...
        s.on_stop()

    Subclasses MAY override:

      - on_start(self, context)
      - on_bar(self, symbol, bar, features) -> Optional[Dict]
      - on_order_filled(self, order, fill)
      - on_stop(self)

    All methods are intentionally synchronous; any async / I/O / broker
    integration should live outside the strategy (router, infra, etc.).
    """

    #: type alias used in docstrings & type hints
    ContextDict = Dict[str, Any]
    BarDict = Dict[str, Any]
    FeatureDict = Dict[str, Any]
    OrderDict = Dict[str, Any]

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Parameters
        ----------
        config:
            Free-form configuration dictionary. Concrete strategies can
            define their expected keys but should be robust to missing ones.
        """
        # Public, mutable config dictionary (backwards compatible)
        self.config: Dict[str, Any] = dict(config or {})
        # Will be set in on_start; kept as plain dict for compatibility
        self.context: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    def get_param(self, key: str, default: Any = None) -> Any:
        """
        Convenience accessor for strategy params.

        Examples
        --------
        size = self.get_param("base_size", 1.0)
        """
        return self.config.get(key, default)

    def set_param(self, key: str, value: Any) -> None:
        """
        Runtime-tunable config parameter. Useful for experiments or
        dynamic control planes.
        """
        self.config[key] = value

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------
    def on_start(self, context: Mapping[str, Any]) -> None:
        """
        Called before backtest/run starts.

        Parameters
        ----------
        context:
            A mapping of shared objects / services, e.g.:

            {
                "feature_store": FeatureStore,
                "tick_store": TickStore,
                "ohlcv_store": OHLCVStore,
                "universe": UniverseService,
                "watchlists": WatchlistService,
                "router": OrderRouter,
                ...
            }

        The default implementation just stores a shallow copy on `self.context`
        so subclasses can read from it later.
        """
        # Store as a plain dict for maximum compatibility with existing code.
        self.context = dict(context)

    def on_bar(
        self,
        symbol: str,
        bar: BarDict,
        features: FeatureDict,
    ) -> Optional[OrderDict]:
        """
        Core strategy callback: called for each new bar.

        Parameters
        ----------
        symbol:
            The instrument symbol (e.g. 'NIFTY', 'BANKNIFTY').
        bar:
            Dict containing OHLCV and any other bar-level info.
            Typical keys: 'open', 'high', 'low', 'close', 'volume', 'ts', ...
        features:
            Dict of derived features for this symbol and timeframe
            from your FeatureStore / screening stack.

        Returns
        -------
        Optional[Dict[str, Any]]:
            - An order-like dict (e.g. {'symbol': ..., 'side': 'BUY', ...})
              if the strategy wants to trade on this bar.
            - None if no action is desired.

        Notes
        -----
        The exact order dict schema is intentionally left to the caller
        (router / execution layer). Strategies should be consistent within
        a project but the base class does not enforce a schema.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.on_bar() must be implemented by subclasses."
        )

    def on_order_filled(
        self,
        order: OrderDict,
        fill: OrderDict,
    ) -> None:
        """
        Notification hook when an order is filled (or partially filled).

        Parameters
        ----------
        order:
            The original order dict that was submitted on behalf of this
            strategy (shape defined by router / execution).
        fill:
            Fill information, e.g. {'qty': ..., 'price': ..., 'side': ...}.

        Default implementation is a no-op; override in concrete strategies
        if you need to maintain internal position state, PnL, etc.
        """
        # No-op by default; subclasses may override.
        return None

    def on_stop(self) -> None:
        """
        Called after the run / backtest / session finishes.

        Override this to:
        - flush any buffers,
        - log final stats,
        - write out diagnostic artifacts, etc.
        """
        # No-op by default; subclasses may override.
        return None
