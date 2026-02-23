# src/router.py
"""
Router / startup helpers for data feeds.

- Uses src.config to obtain selected token/client id/ws url automatically.
- start_dhan_v2_feed() can be called without parameters and will use values from src.config:
    config.selected_token, config.selected_client_id, config.selected_ws_url
- Accepts both 'instruments' (alias used by tools/start_data_feed) and 'request_instruments'.
- register_market_handler(fn) lets strategies receive normalized dicts from the feed.
"""

from __future__ import annotations
import logging
import threading
from typing import Callable, Optional, List, Dict, Any

from src.config import config
# Import the DhanV2Feed implementation you have in src/feeds/dhan_v2_feed.py
try:
    from src.feeds.dhan_v2_feed import DhanV2Feed
except Exception:
    DhanV2Feed = None

_logger = logging.getLogger(__name__)

# Module-level feed instance (single active feed per router)
_feed_instance: Optional["DhanV2Feed"] = None
_feed_lock = threading.Lock()

# Market handler callback: receives normalized dicts from feed (market events)
_market_handler: Optional[Callable[[dict], None]] = None


def register_market_handler(fn: Callable[[dict], None]) -> None:
    """
    Register a market handler (strategy) to receive normalized market dicts.
    Example:
        def my_handler(event: dict):
            pass
        register_market_handler(my_handler)
    """
    global _market_handler
    _market_handler = fn
    _logger.info("Registered market handler: %s", getattr(fn, "__name__", str(fn)))


def _dispatch_to_handler(event: dict) -> None:
    if _market_handler:
        try:
            _market_handler(event)
        except Exception:
            _logger.exception("Market handler raised an exception")


def start_dhan_v2_feed(token: Optional[str] = None,
                       client_id: Optional[str] = None,
                       ws_url: Optional[str] = None,
                       rest_base: Optional[str] = None,
                       background: bool = True,
                       request_instruments: Optional[List[Dict[str, str]]] = None,
                       instruments: Optional[List[Dict[str, str]]] = None,
                       **feed_kwargs) -> "DhanV2Feed":
    """
    Start (or reuse) a Dhan v2 feed instance.

    Parameters:
      - token, client_id, ws_url, rest_base: optional overrides (otherwise read from config)
      - background: start feed in background thread when True
      - request_instruments / instruments: list of instrument dicts to subscribe (alias support)
      - feed_kwargs: passed to DhanV2Feed constructor

    If token/client_id/ws_url are not provided, the function will use values from src.config:
      config.selected_token, config.selected_client_id, config.selected_ws_url

    Returns the feed instance (running). If background=True the feed will start in a background thread.
    """
    global _feed_instance

    with _feed_lock:
        if _feed_instance:
            _logger.info("Reusing existing Dhan v2 feed instance (client=%s)", getattr(_feed_instance, "client_id", "unknown"))
            return _feed_instance

        # select values from args or config
        token = token or config.selected_token
        client_id = client_id or config.selected_client_id
        ws_url = ws_url or config.selected_ws_url
        rest_base = rest_base or config.selected_rest_base

        # Prefer explicit parameter; accept 'instruments' (tools/start_data_feed) as alias
        final_instruments = request_instruments if request_instruments is not None else instruments
        if final_instruments is None:
            final_instruments = getattr(config, "DHAN_V2_INSTRUMENTS", [])

        if not token or not client_id:
            raise RuntimeError("Missing token or client_id. Set them in .env or pass explicitly to start_dhan_v2_feed()")

        # Determine endpoint for DhanV2Feed:
        # If ws_url is a full URL with query (contains '?'), strip query and use base endpoint.
        if ws_url and "?" in ws_url:
            endpoint = ws_url.split("?", 1)[0]
        else:
            endpoint = ws_url or "wss://api-feed.dhan.co"

        if DhanV2Feed is None:
            raise RuntimeError("DhanV2Feed implementation not importable. Check src/feeds/dhan_v2_feed.py")

        _logger.info("Starting Dhan v2 feed (client_id=%s) endpoint=%s", client_id, endpoint)
        _logger.debug("Using token=%s, instruments=%d", ("<present>" if token else "<missing>"), len(final_instruments))

        try:
            _feed_instance = DhanV2Feed(
                token=token,
                client_id=client_id,
                request_instruments=final_instruments,
                endpoint=endpoint,
                on_message=_dispatch_to_handler,
                **feed_kwargs,
            )
        except TypeError as te:
            # Defensive: if constructor signature differs, try to pass instruments under other names
            _logger.exception("Error instantiating DhanV2Feed (TypeError). Attempting fallback ctor signatures.")
            # Try a few fallbacks that older/newer implementations might expect
            tried = False
            try:
                _feed_instance = DhanV2Feed(token=token, client_id=client_id, instruments=final_instruments, endpoint=endpoint, on_message=_dispatch_to_handler, **feed_kwargs)
                tried = True
            except Exception:
                _logger.debug("Fallback ctor with 'instruments' failed; trying 'request_instruments' (already tried).")
            if not tried:
                raise

        # start the feed: feed exposes start_background() and run_forever()
        try:
            if background:
                if hasattr(_feed_instance, "start_background"):
                    _feed_instance.start_background()
                else:
                    # fallback to a thread that runs run_forever()
                    def _run_blocking():
                        try:
                            _feed_instance.run_forever()
                        except Exception:
                            _logger.exception("Feed run_forever() raised")

                    th = threading.Thread(target=_run_blocking, name="dhan-v2-run", daemon=True)
                    th.start()
            else:
                # blocking start
                if hasattr(_feed_instance, "run_forever"):
                    _feed_instance.run_forever()
                elif hasattr(_feed_instance, "start_background"):
                    _feed_instance.start_background()
        except Exception:
            _logger.exception("Error while starting DhanV2Feed")

        _logger.info("Dhan v2 feed started (background=%s) client=%s instruments=%s", background, client_id, len(final_instruments))
        return _feed_instance


def stop_dhan_v2_feed() -> None:
    """
    Stop the feed if running and clear the module-level instance.
    """
    global _feed_instance
    with _feed_lock:
        if not _feed_instance:
            _logger.info("No feed instance to stop")
            return
        try:
            _logger.info("Stopping Dhan v2 feed (client=%s)", getattr(_feed_instance, "client_id", "unknown"))
            if hasattr(_feed_instance, "stop"):
                _feed_instance.stop()
            else:
                _logger.info("Feed object has no stop() method; attempting run loop stop if available")
                try:
                    if hasattr(_feed_instance, "_loop") and _feed_instance._loop.is_running():
                        _feed_instance._loop.call_soon_threadsafe(_feed_instance._loop.stop)
                except Exception:
                    _logger.exception("Error trying to stop feed loop")
        except Exception:
            _logger.exception("Exception while stopping feed")
        finally:
            _feed_instance = None
            _logger.info("Dhan v2 feed stopped and instance cleared.")
