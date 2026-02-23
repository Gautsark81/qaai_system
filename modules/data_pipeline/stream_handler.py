# modules/data_pipeline/stream_handler.py

"""
Stream Handler

Stability-first:
- No mutation
- No side effects beyond alert emission
"""

from typing import Any


def handle_stream_event(
    symbol: str,
    bar: Any,
    prev_bar: Any,
    market_data_guard,
    alert_manager,
) -> bool:
    if market_data_guard is None:
        return False

    if not market_data_guard.validate(symbol, bar, prev_bar):
        if alert_manager:
            alert_manager.emit(
                severity="WARN",
                category="DATA",
                message="Market data blocked",
                context={"symbol": symbol},
            )
        return False

    return True