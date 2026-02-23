# providers/dhan_client.py
"""
Robust Dhan provider wrapper.
- Tries to instantiate the installed `dhanhq` package using multiple known entrypoints.
- Provides REST fallbacks when client methods are missing.
- Provides WebSocket fallback that does NOT rely on passing extra_headers to loop.create_connection
  (instead sends auth/subscribe messages after connecting) — this avoids Windows create_connection extra_headers errors.
"""

from __future__ import annotations
import logging
import asyncio
import json
import os
from typing import Iterable, Callable, Any

logger = logging.getLogger("providers.dhan_client")
logger.setLevel(logging.INFO)

# read credentials from env_config
try:
    from env_config import DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN, DHAN_BASE_URL, DHAN_WS_URL
except Exception:
    # fallback to environment variables if env_config not set up as module
    DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "")
    DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "")
    DHAN_BASE_URL = os.getenv("DHAN_BASE_URL", "https://api.dhan.co")
    DHAN_WS_URL = os.getenv("DHAN_WS_URL", "wss://push.dhan.co/marketfeed")

# try to import dhanhq; it might be a module with attributes rather than a callable
try:
    import dhanhq as _dhanhq_mod  # type: ignore
except Exception:
    _dhanhq_mod = None

# websockets fallback
try:
    import websockets  # type: ignore
except Exception:
    websockets = None  # type: ignore

# requests fallback for REST
import requests  # pip installed earlier


class DhanClient:
    def __init__(self):
        if not DHAN_CLIENT_ID or not DHAN_ACCESS_TOKEN:
            raise ValueError("Missing DHAN_CLIENT_ID/DHAN_ACCESS_TOKEN")

        self.client = None
        self._supports_feed = False

        # Try to instantiate the dhanhq client using a few known patterns
        if _dhanhq_mod:
            try:
                # 1) module exposes a callable class at dhanhq.dhanhq (common packaging)
                if hasattr(_dhanhq_mod, "dhanhq") and callable(
                    getattr(_dhanhq_mod, "dhanhq")
                ):
                    self.client = getattr(_dhanhq_mod, "dhanhq")(
                        DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN
                    )
                # 2) module itself might expose a class named Dhan or DhanHQ
                elif hasattr(_dhanhq_mod, "Dhan") and callable(
                    getattr(_dhanhq_mod, "Dhan")
                ):
                    self.client = getattr(_dhanhq_mod, "Dhan")(
                        DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN
                    )
                elif hasattr(_dhanhq_mod, "DhanHQ") and callable(
                    getattr(_dhanhq_mod, "DhanHQ")
                ):
                    self.client = getattr(_dhanhq_mod, "DhanHQ")(
                        DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN
                    )
                # 3) some versions expect only token
                elif callable(_dhanhq_mod):
                    try:
                        self.client = _dhanhq_mod(DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN)
                    except Exception:
                        self.client = _dhanhq_mod(DHAN_ACCESS_TOKEN)
                else:
                    # As a last resort, inspect attributes for useful methods
                    # if module contains functions like get_positions, we can use it as-is:
                    if any(
                        n in dir(_dhanhq_mod)
                        for n in ("get_positions", "get_historical_data", "place_order")
                    ):
                        # keep module as client for direct calls
                        self.client = _dhanhq_mod
            except Exception as ex:
                logger.warning("Could not instantiate dhanhq client: %s", ex)
                self.client = None

        # Detect built-in feed API on the client object if present
        if self.client is not None:
            for name in (
                "initiate_market_feed",
                "start_market_feed",
                "market_feed",
                "marketfeed",
                "subscribe",
            ):
                if hasattr(self.client, name):
                    self._supports_feed = True
                    self._feed_method_name = name
                    logger.info("dhanhq client supports feed via: %s", name)
                    break

        # If websockets isn't available and we don't have built-in feed, warn.
        if not self._supports_feed and websockets is None:
            logger.warning(
                "No feed support detected and websockets not installed; install websockets for fallback"
            )

    # ----- REST wrappers -----
    def get_positions(self) -> Any:
        if self.client is not None and hasattr(self.client, "get_positions"):
            return getattr(self.client, "get_positions")()
        # fallback to REST
        url = DHAN_BASE_URL.rstrip("/") + "/v2/positions"
        headers = {"client-id": DHAN_CLIENT_ID, "access-token": DHAN_ACCESS_TOKEN}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()

    def get_holdings(self) -> Any:
        if self.client is not None and hasattr(self.client, "get_holdings"):
            return getattr(self.client, "get_holdings")()
        url = DHAN_BASE_URL.rstrip("/") + "/v2/holdings"
        headers = {"client-id": DHAN_CLIENT_ID, "access-token": DHAN_ACCESS_TOKEN}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()

    def place_order(self, payload_or_symbol, *args, **kwargs) -> Any:
        # accept dict or (symbol, side, qty, price)
        if isinstance(payload_or_symbol, dict):
            payload = payload_or_symbol
        else:
            symbol = payload_or_symbol
            side = args[0] if len(args) >= 1 else kwargs.get("side")
            qty = args[1] if len(args) >= 2 else kwargs.get("qty")
            price = kwargs.get("price", None)
            payload = {
                "exchange_segment": "NSE_EQ",
                "security_id": symbol,
                "transaction_type": (
                    "BUY" if str(side).lower().startswith("b") else "SELL"
                ),
                "order_type": "MARKET" if price is None else "LIMIT",
                "quantity": int(qty),
                "product_type": kwargs.get("product_type", "INTRADAY"),
            }
            if price is not None:
                payload["price"] = float(price)

        # try client.place_order first
        if self.client is not None and hasattr(self.client, "place_order"):
            return getattr(self.client, "place_order")(payload)
        # fallback to REST
        url = DHAN_BASE_URL.rstrip("/") + "/v2/orders"
        headers = {
            "client-id": DHAN_CLIENT_ID,
            "access-token": DHAN_ACCESS_TOKEN,
            "Content-Type": "application/json",
        }
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()

    def get_ohlc(self, symbol: str, interval: str = "1MIN") -> Any:
        if self.client is not None and hasattr(self.client, "get_historical_data"):
            return getattr(self.client, "get_historical_data")(
                security_id=f"NSE_EQ:{symbol}", interval=interval
            )
        url = DHAN_BASE_URL.rstrip("/") + "/v2/marketfeed/ohlc"
        headers = {"client-id": DHAN_CLIENT_ID, "access-token": DHAN_ACCESS_TOKEN}
        payload = {"security_id": f"NSE_EQ:{symbol}", "interval": interval}
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    # ----- Feed subscription -----
    def subscribe_market_feed(
        self,
        symbols: Iterable[str],
        callback: Callable[[dict], None],
        run_forever: bool = True,
    ):
        """
        Blocking wrapper calling the async version.
        """
        asyncio.run(
            self.subscribe_market_feed_async(symbols, callback, run_forever=run_forever)
        )

    async def subscribe_market_feed_async(
        self,
        symbols: Iterable[str],
        callback: Callable[[dict], None],
        run_forever: bool = True,
    ):
        """
        Fallback websocket subscription. DOES NOT pass extra_headers to websockets.connect
        to avoid Windows create_connection extra_headers error.
        Instead it connects, then sends an auth message or subscribe message per Dhan API.
        """
        if self._supports_feed and self.client is not None:
            # call library's feed method in a thread or coroutine depending on signature
            fn = getattr(self.client, self._feed_method_name)
            logger.info("Using client-provided feed method: %s", self._feed_method_name)
            # some client feed methods are blocking, some are async; try to call safely
            try:
                result = fn(
                    [s if ":" in s else f"NSE_EQ:{s}" for s in symbols], callback
                )
                # if result is awaitable, await it
                if asyncio.iscoroutine(result):
                    await result
                return
            except Exception as e:
                logger.warning(
                    "Built-in feed method failed; falling back to websocket: %s", e
                )

        if websockets is None:
            raise RuntimeError(
                "websockets not installed; install websockets to use WS fallback"
            )

        url = os.getenv("DHAN_WS_URL", DHAN_WS_URL)
        full_syms = [s if ":" in s else f"NSE_EQ:{s}" for s in symbols]

        async def _connect_and_run():
            backoff = 1
            while True:
                try:
                    logger.info("Connecting to %s (no extra_headers mode)", url)
                    # connect without passing extra_headers to avoid BaseEventLoop.create_connection errors on Windows
                    async with websockets.connect(
                        url, ping_interval=20, ping_timeout=10
                    ) as ws:
                        # After connection, send an auth message if Dhan expects it, or send subscribe
                        # Many Dhan examples use header auth; if headers are required by the server we must use them,
                        # but to be compatible we first try sending an auth payload.
                        try:
                            auth_msg = {
                                "type": "auth",
                                "access-token": DHAN_ACCESS_TOKEN,
                                "client-id": DHAN_CLIENT_ID,
                            }
                            await ws.send(json.dumps(auth_msg))
                        except Exception:
                            # server may ignore auth payload; continue
                            logger.debug("Auth payload send failed or not needed")

                        # send subscribe payload (documented protocol may vary; adapt to API doc)
                        subscribe_payload = {
                            "type": "subscribe",
                            "instruments": full_syms,
                        }
                        await ws.send(json.dumps(subscribe_payload))
                        logger.info("Subscribe payload sent: %s", subscribe_payload)
                        async for raw in ws:
                            try:
                                parsed = json.loads(raw)
                                # schedule callback
                                asyncio.create_task(self._safe_cb(callback, parsed))
                            except Exception:
                                logger.exception("Failed to parse WS message")
                except Exception as e:
                    logger.warning(
                        "WS connection error: %s — retrying in %s seconds", e, backoff
                    )
                    await asyncio.sleep(backoff)
                    backoff = min(60, backoff * 2)
                if not run_forever:
                    break

        await _connect_and_run()

    async def _safe_cb(self, cb, parsed):
        try:
            cb(parsed)
        except Exception:
            logger.exception("User callback error")
