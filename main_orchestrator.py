"""
Shim module for backwards-compatibility with legacy tests.

Tests refer to `main_orchestrator.*`, but the real implementation now
lives in `legacy_main_orchestrator.py`.
"""

from legacy_main_orchestrator import (
    run_trading_pipeline_once,
    # the following are only used as patch targets in tests:
    fetch_price_data,
    build_watchlist,
    generate_signals,
    OrderManager,
    BrokerAdapter,
)

__all__ = [
    "run_trading_pipeline_once",
    "fetch_price_data",
    "build_watchlist",
    "generate_signals",
    "OrderManager",
    "BrokerAdapter",
]
