"""
Strategy Factory
================

Authoritative strategy registry and construction layer.

Key principle:
- STRICT validation for execution (create)
- FULLY ADAPTIVE construction for tests/examples (from_config)

This separation is intentional and REQUIRED.
"""

from __future__ import annotations

import inspect
from typing import Dict, Type, Any, List


# =============================================================================
# Execution Interface Contract (PRODUCTION ONLY)
# =============================================================================

EXECUTION_REQUIRED_METHODS = {
    "initialize",
    "on_tick",
    "on_bar",
    "generate_signal",
}


# =============================================================================
# Registry
# =============================================================================

_STRATEGY_REGISTRY: Dict[str, Type] = {}


# =============================================================================
# Exceptions
# =============================================================================

class StrategyRegistrationError(RuntimeError):
    pass


class StrategyValidationError(RuntimeError):
    pass


# =============================================================================
# Decorator
# =============================================================================

def register_strategy(name: str):
    def decorator(cls: Type) -> Type:
        StrategyFactory.register(name, cls)
        return cls
    return decorator


# =============================================================================
# Factory
# =============================================================================

class StrategyFactory:
    """
    Central strategy registry and constructor.
    """

    # ------------------------------------------------------------------
    # Registration (LENIENT)
    # ------------------------------------------------------------------

    @staticmethod
    def register(name: str, cls: Type) -> None:
        if not isinstance(name, str) or not name:
            raise StrategyRegistrationError("Strategy name must be non-empty")

        if name in _STRATEGY_REGISTRY:
            raise StrategyRegistrationError(
                f"Strategy '{name}' already registered"
            )

        if not inspect.isclass(cls):
            raise StrategyRegistrationError(
                f"Strategy '{name}' must be a class"
            )

        _STRATEGY_REGISTRY[name] = cls

    # ------------------------------------------------------------------
    # STRICT EXECUTION CONSTRUCTION
    # ------------------------------------------------------------------

    @staticmethod
    def create(name: str, **kwargs: Any) -> Any:
        if name not in _STRATEGY_REGISTRY:
            raise StrategyValidationError(
                f"Unknown strategy '{name}'. "
                f"Available: {StrategyFactory.list_registered()}"
            )

        cls = _STRATEGY_REGISTRY[name]
        StrategyFactory._validate_execution_interface(cls, name)

        try:
            return cls(**kwargs)
        except TypeError as e:
            raise StrategyValidationError(
                f"Failed to construct strategy '{name}': {e}"
            ) from e

    # ------------------------------------------------------------------
    # FULLY ADAPTIVE CONSTRUCTION (TESTS / EXAMPLES)
    # ------------------------------------------------------------------

    @staticmethod
    def from_config(cfg: dict) -> Any:
        if not isinstance(cfg, dict):
            raise StrategyValidationError("Strategy config must be a dict")

        if "type" not in cfg:
            raise StrategyValidationError("Strategy config missing 'type'")

        name = cfg["type"]
        params = cfg.get("params", {}) or {}
        strategy_id = cfg.get("strategy_id")

        if name not in _STRATEGY_REGISTRY:
            raise StrategyValidationError(
                f"Unknown strategy '{name}'. "
                f"Available: {StrategyFactory.list_registered()}"
            )

        cls = _STRATEGY_REGISTRY[name]

        # --- Try positional + dict-based constructors (legacy-safe) ---
        constructors = [
            lambda: cls(strategy_id, params),
            lambda: cls(params),
            lambda: cls(cfg),
            lambda: cls(strategy_id=strategy_id, **StrategyFactory._filter_kwargs(cls, params)),
            lambda: cls(**StrategyFactory._filter_kwargs(cls, params)),
            lambda: cls(),
        ]

        instance = None
        for ctor in constructors:
            try:
                instance = ctor()
                break
            except TypeError:
                continue

        if instance is None:
            raise StrategyValidationError(
                f"Unable to construct strategy '{name}' "
                f"using adaptive construction. "
                f"params={params}"
            )

        # --- Attribute injection fallback ---
        for k, v in params.items():
            if not hasattr(instance, k):
                try:
                    setattr(instance, k, v)
                except Exception:
                    pass

        if strategy_id is not None and not hasattr(instance, "strategy_id"):
            try:
                setattr(instance, "strategy_id", strategy_id)
            except Exception:
                pass

        return instance

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _filter_kwargs(cls: Type, params: dict) -> dict:
        """
        Filters params to only those accepted by __init__ signature.
        """
        try:
            sig = inspect.signature(cls.__init__)
            return {
                k: v for k, v in params.items()
                if k in sig.parameters
            }
        except Exception:
            return {}

    # ------------------------------------------------------------------
    # Validation (STRICT)
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_execution_interface(cls: Type, name: str) -> None:
        missing = [
            m for m in EXECUTION_REQUIRED_METHODS
            if not callable(getattr(cls, m, None))
        ]
        if missing:
            raise StrategyValidationError(
                f"Strategy '{name}' is not executable. "
                f"Missing required methods: {missing}"
            )

    # ------------------------------------------------------------------
    # Introspection / Test utilities
    # ------------------------------------------------------------------

    @staticmethod
    def list_registered() -> List[str]:
        return sorted(_STRATEGY_REGISTRY.keys())

    @staticmethod
    def clear() -> None:
        _STRATEGY_REGISTRY.clear()
