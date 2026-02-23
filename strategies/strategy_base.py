# strategies/strategy_base.py
"""
Canonical Strategy base implementation for the /strategies package.

This module provides:
  - StrategyBase: a minimal base class for strategies.
  - register_strategy: decorator to register strategy classes by name.
  - get_registered_strategy: lookup helper.

Place concrete strategy implementations in /strategies (e.g. strategies/sma_strategy.py)
and register them using the `@register_strategy("name")` decorator.
"""
from typing import Any, Dict, Optional, Callable, List
import logging

logger = logging.getLogger("strategies.strategy_base")

# Simple in-memory registry for strategy classes
_STRATEGY_REGISTRY: Dict[str, Callable[..., Any]] = {}


def register_strategy(name: str):
    """Decorator to register a strategy class under a given name."""
    def _decorator(cls):
        _STRATEGY_REGISTRY[name] = cls
        logger.debug("Registered strategy %s -> %s", name, cls)
        return cls
    return _decorator


def get_registered_strategy(name: str) -> Optional[Callable[..., Any]]:
    """Return the registered strategy class for `name` or None."""
    return _STRATEGY_REGISTRY.get(name)


class StrategyBase:
    """Minimal strategy base class.

    Concrete strategies should implement:
      - generate_signals(self, market_state) -> List[Dict[str, Any]]
      - on_fill(self, fill_event) -> None
    """

    def __init__(
        self,
        sid_or_config: Optional[Any] = None,
        allocation: float = 1.0,
        per_symbol_cap: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Backwards-compatible initializer.

        Supported call styles:
          - StrategyBase(sid: str, allocation=1.0, per_symbol_cap=None, config=None)
          - StrategyBase(config: dict)  # config may contain "strategy_id"

        This covers tests and existing code that pass 'sid' + allocation keywords.
        """
        # If the first positional arg is a dict, treat it as config
        if isinstance(sid_or_config, dict) and config is None:
            config = sid_or_config
            sid = config.get("strategy_id") or self.__class__.__name__
        else:
            sid = sid_or_config or self.__class__.__name__

        self.id: str = sid
        self.allocation: float = allocation
        self.per_symbol_cap: Optional[int] = per_symbol_cap
        self.config: Dict[str, Any] = config or {}
        self.state: Dict[str, Any] = {}
        logger.debug(
            "StrategyBase initialized id=%s allocation=%s per_symbol_cap=%s",
            self.id,
            self.allocation,
            self.per_symbol_cap,
        )

    def generate_signals(self, market_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return a list of signal dictionaries. Must be implemented by subclasses."""
        raise NotImplementedError("generate_signals must be implemented by concrete strategies")

    def on_fill(self, fill_event: Dict[str, Any]) -> None:
        """Callback invoked on order fill events. Default is no-op."""
        logger.debug("on_fill called for %s: %s", self.id, fill_event)

    def snapshot(self) -> Dict[str, Any]:
        """Return a serializable snapshot for audits/tests."""
        return {"id": self.id, "config": self.config, "state": self.state}


__all__ = ["StrategyBase", "register_strategy", "get_registered_strategy"]
