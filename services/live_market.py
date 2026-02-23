"""
Dhan v2 live market feed service.

- Connects to Dhan MarketFeed (dhanhq==2.1.0, WebSocket v2).
- Streams ticks into Redis channel `market:ticks`.
- Optionally prints live ticks to console so you can visually verify feed.

Usage (from project root):
    python Live_market.py
or:
    python -m services.live_market
"""

from __future__ import annotations

import json
import logging
import os
import random
import signal
import time
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv

# Load root env file; override any OS-level leftovers
load_dotenv(override=True)

# ===============================
# Config & env for Dhan v2 live feed
# ===============================

# Core credentials
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

# REST base + API version
DHAN_REST_BASE = os.getenv("DHAN_REST_BASE", "https://api.dhan.co")
DHAN_API_VERSION = os.getenv("DHAN_API_VERSION", "v2")

# Instrument list (v2 style)
# Format: SEGMENT:SECID or SEGMENT:SECID:SubscriptionType
# Example: "NSE_EQ:1333,NSE_EQ:11915:Full,BSE_EQ:532540:Quote"
DHAN_V2_INSTRUMENTS = os.getenv(
    "DHAN_V2_INSTRUMENTS",
    "NSE_EQ:1333,NSE_EQ:11915:Full",
)

# Default subscription when not specified in token
DHAN_SUBSCRIPTION_DEFAULT = os.getenv("DHAN_SUBSCRIPTION_DEFAULT", "Ticker")

# Redis settings
REDIS_URL = os.getenv("REDIS_URL")
REDIS_CHANNEL = os.getenv("LIVE_MARKET_REDIS_CHANNEL", "market:ticks")

# Whether we are in safe mode — feed only, no trading logic (for future)
SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() in ("1", "true", "yes")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Health file path (touch file updated to indicate running/healthy)
HEALTHFILE = os.getenv("LIVE_MARKET_HEALTHFILE", "/tmp/live_market.healthy")

# Backoff params
BACKOFF_INITIAL = float(os.getenv("BACKOFF_INITIAL", "1.0"))
BACKOFF_MAX = float(os.getenv("BACKOFF_MAX", "60.0"))
BACKOFF_JITTER = float(os.getenv("BACKOFF_JITTER", "0.25"))  # fraction of backoff

# Console tick printing for debugging
PRINT_TICKS = os.getenv("LIVE_MARKET_PRINT_TICKS", "true").lower() in (
    "1",
    "true",
    "yes",
)
PRINT_TICKS_LIMIT = int(os.getenv("LIVE_MARKET_PRINT_TICKS_LIMIT", "0"))  # 0 = no cap

# ===============================
# Logging config
# ===============================
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("live.market")

# ===============================
# Redis client (optional)
# ===============================
redis_client = None
if REDIS_URL:
    try:
        import redis

        redis_client = redis.from_url(REDIS_URL)
        # Quick ping to check connection (not fatal if fails)
        try:
            redis_client.ping()
            logger.info("Connected to Redis at %s", REDIS_URL)
        except Exception as e:  # pragma: no cover - just logging
            logger.warning("Redis ping failed: %s — continuing without Redis", e)
            redis_client = None
    except Exception as e:  # pragma: no cover - just logging
        logger.warning("Redis library not available or connection failed: %s", e)
        redis_client = None

# Graceful shutdown flag
_shutdown_requested = False

# Counter for console tick prints
_printed_ticks = 0


def _on_signal(signum, frame) -> None:
    global _shutdown_requested
    logger.info("Signal %s received — requesting shutdown", signum)
    _shutdown_requested = True


signal.signal(signal.SIGINT, _on_signal)
signal.signal(signal.SIGTERM, _on_signal)

# ===============================
# Token parsing helpers
# ===============================


def parse_token(token: str) -> Tuple[str, str, Optional[str]]:
    """
    Parse an instrument token.
    Acceptable forms:
      - SEG:SECID
      - SEG:SECID:Subscription (e.g. NSE_EQ:1333:Full)
    Returns (segment, secid, subscription_or_None)
    """
    parts = token.split(":")
    if len(parts) == 2:
        seg, secid = parts
        return seg.strip(), secid.strip(), None
    elif len(parts) == 3:
        seg, secid, sub = parts
        return seg.strip(), secid.strip(), sub.strip()
    else:
        raise ValueError(f"Invalid instrument token: {token!r}")


def map_segment(MF, name: str):
    """
    Map common segment strings to MarketFeed constants.
    MF is expected to be the MarketFeed class from Dhan SDK.
    """
    name = (name or "").upper()
    mapping = {
        "NSE_EQ": getattr(MF, "NSE", None),
        "NSE": getattr(MF, "NSE", None),
        "BSE_EQ": getattr(MF, "BSE", None),
        "BSE": getattr(MF, "BSE", None),
        "NSE_FNO": getattr(MF, "NSE_FNO", None),
        "NSE_FO": getattr(MF, "NSE_FNO", None),
        "NSE_CURRENCY": getattr(MF, "CUR", None),
        "MCX_COMM": getattr(MF, "MCX", None),
    }
    return mapping.get(name)


def map_subscription(MF, sub: Optional[str]):
    """
    Map subscription strings (Ticker / Quote / Full) to MarketFeed constants.
    If sub is None, use DHAN_SUBSCRIPTION_DEFAULT.
    """
    if not sub:
        sub = DHAN_SUBSCRIPTION_DEFAULT
    sub = sub.lower()
    mapping = {
        "ticker": getattr(MF, "Ticker", None),
        "quote": getattr(MF, "Quote", None),
        "full": getattr(MF, "Full", None),
    }
    return mapping.get(sub)


# ===============================
# Health file
# ===============================


def touch_healthfile() -> None:
    """Update the healthfile timestamp to signal liveness."""
    if not HEALTHFILE:
        return
    try:
        os.makedirs(os.path.dirname(HEALTHFILE), exist_ok=True)
        with open(HEALTHFILE, "w", encoding="utf-8") as f:
            f.write(str(time.time()))
    except Exception as e:  # pragma: no cover - just logging
        logger.debug("Failed to touch healthfile %s: %s", HEALTHFILE, e)


# ===============================
# Tick normalization & publishing
# ===============================


def normalize_tick(pkt: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Dhan's MarketFeed packet into a stable schema for consumers
    (screeners, watchlists, strategy runners).

    Redis JSON schema on `market:ticks` channel:

        {
          "ts": 1733300000000,            # epoch millis when we processed tick
          "exchange_segment": "NSE_EQ",   # e.g. NSE_EQ, BSE_EQ, NSE_FNO
          "security_id": "1333",          # Dhan security id as string
          "ltp": 4750.25,                 # last traded price
          "open": 4700.0,
          "high": 4780.0,
          "low": 4690.0,
          "close": 4725.0,
          "volume": 123456,               # traded volume if provided
          "raw": { ... }                  # original packet from Dhan
        }
    """
    now_ms = int(time.time() * 1000)

    def _first(*keys):
        for k in keys:
            if k in pkt and pkt[k] is not None:
                return pkt[k]
        return None

    exch = _first("exchange_segment", "ExchangeSegment", "exchangeSegment")
    secid = _first("security_id", "SecurityId", "securityId")
    ltp = _first("LTP", "ltp", "last_price", "LastTradedPrice", "lastTradedPrice")
    o = _first("open", "Open")
    h = _first("high", "High")
    l = _first("low", "Low")
    c = _first("close", "Close")
    vol = _first("volume", "Volume", "total_trade_volume", "totalTradeVolume")

    norm: Dict[str, Any] = {
        "ts": now_ms,
        "exchange_segment": exch,
        "security_id": str(secid) if secid is not None else None,
        "ltp": float(ltp) if ltp is not None else None,
        "open": float(o) if o is not None else None,
        "high": float(h) if h is not None else None,
        "low": float(l) if l is not None else None,
        "close": float(c) if c is not None else None,
        "volume": int(vol) if isinstance(vol, (int, float)) else vol,
        "raw": pkt,
    }
    return norm


def publish_tick(pkt: Dict[str, Any]) -> None:
    """
    Normalize tick, publish to Redis, and optionally print to console.
    """
    global _printed_ticks

    if not isinstance(pkt, dict):
        logger.debug("Skipping non-dict packet from MarketFeed: %r", pkt)
        return

    tick = normalize_tick(pkt)

    # Publish to Redis channel
    if redis_client is not None:
        try:
            redis_client.publish(REDIS_CHANNEL, json.dumps(tick, default=str))
        except Exception as e:  # pragma: no cover - just logging
            logger.warning("Failed to publish tick to Redis: %s", e)

    # Optionally print to console so you SEE live data in PowerShell
    if PRINT_TICKS:
        if PRINT_TICKS_LIMIT and _printed_ticks >= PRINT_TICKS_LIMIT:
            return
        _printed_ticks += 1

        exch = tick.get("exchange_segment") or "?"
        secid = tick.get("security_id") or "?"
        ltp = tick.get("ltp")
        o = tick.get("open")
        h = tick.get("high")
        l = tick.get("low")
        c = tick.get("close")
        vol = tick.get("volume")

        msg = (
            f"TICK #{_printed_ticks} "
            f"{exch}:{secid} "
            f"LTP={ltp} O={o} H={h} L={l} C={c} Vol={vol}"
        )
        logger.info(msg)


# ===============================
# Main runner
# ===============================


def run() -> None:
    """
    Main loop: connect to Dhan MarketFeed v2 and stream ticks.

    Pattern is based on official v2.1.0 example:

        data = MarketFeed(dhan_context, instruments, "v2")
        while True:
            data.run_forever()
            response = data.get_data()
            print(response)
    """
    from dhanhq import DhanContext, MarketFeed

    if not DHAN_CLIENT_ID or not DHAN_ACCESS_TOKEN:
        logger.error(
            "DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN missing. "
            "Set them in root .env or environment."
        )
        raise SystemExit(1)

    # Build instruments list from DHAN_V2_INSTRUMENTS
    tokens = [x.strip() for x in DHAN_V2_INSTRUMENTS.split(",") if x.strip()]
    instruments = []
    for tok in tokens:
        try:
            seg, secid, sub = parse_token(tok)
        except Exception as e:
            logger.warning("Skipping instrument token %r: %s", tok, e)
            continue
        seg_const = map_segment(MarketFeed, seg)
        if seg_const is None:
            logger.warning("Unknown segment for token %s -> %s", tok, seg)
            continue
        sub_const = map_subscription(MarketFeed, sub)
        instruments.append((seg_const, secid, sub_const))

    if not instruments:
        logger.error(
            "No valid instruments parsed from DHAN_V2_INSTRUMENTS (%r). Exiting.",
            DHAN_V2_INSTRUMENTS,
        )
        raise SystemExit(1)

    logger.info("Will subscribe to %d instruments: %s", len(instruments), instruments)

    backoff = BACKOFF_INITIAL

    # Outer reconnect loop
    while not _shutdown_requested:
        feed = None
        try:
            # Fresh context each reconnect
            ctx = DhanContext(DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN)
            logger.info(
                "DhanContext initialized (client_id=%s) using API %s",
                DHAN_CLIENT_ID,
                DHAN_API_VERSION,
            )

            feed = MarketFeed(ctx, instruments, DHAN_API_VERSION)

            # According to docs, run_forever() starts the internal WS loop.
            # For v2.1.0 this should return quickly / non-blocking, then we
            # continuously pull data with get_data().
            logger.info("Starting feed.run_forever() (v2 market feed)")
            feed.run_forever()

            # Reset backoff after successful start
            backoff = BACKOFF_INITIAL

            # Inner loop: continuously drain get_data()
            while not _shutdown_requested:
                try:
                    pkt = feed.get_data()
                except Exception as e:
                    logger.exception("Error getting data from market feed: %s", e)
                    break

                if not pkt:
                    # No data right now. Check if server signalled close.
                    if getattr(feed, "on_close", False):
                        logger.warning(
                            "Feed on_close signalled by SDK — will reconnect."
                        )
                        break
                    # Small sleep to avoid busy-spin when idle
                    time.sleep(0.05)
                    continue

                # Some modes may return list or single dict
                if isinstance(pkt, list):
                    for p in pkt:
                        publish_tick(p)
                else:
                    publish_tick(pkt)

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt — shutting down live market.")
            break
        except Exception as e:
            logger.exception("Market feed error: %s", e)
        finally:
            # Try to disconnect cleanly if SDK supports it
            try:
                if feed is not None and hasattr(feed, "disconnect"):
                    feed.disconnect()
            except Exception:
                pass

        if _shutdown_requested:
            break

        # Exponential backoff + jitter before reconnect
        jitter = backoff * BACKOFF_JITTER * (random.random() - 0.5) * 2
        wait = min(BACKOFF_MAX, backoff + jitter)
        logger.warning("Feed disconnected — reconnecting in %.1f seconds", wait)
        touch_healthfile()
        time.sleep(max(0.1, wait))
        backoff = min(BACKOFF_MAX, backoff * 2)

    logger.info("Live market runner stopped.")


# -------------------------------
# CLI entrypoint
# -------------------------------
if __name__ == "__main__":
    logger.info("Starting live_market runner (safe_mode=%s)", SAFE_MODE)
    touch_healthfile()
    try:
        run()
    except SystemExit:
        raise
    except Exception as e:  # pragma: no cover
        logger.exception("Unhandled error in live_market runner: %s", e)
        raise
