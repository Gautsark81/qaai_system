"""
Dhan WS ingestion with handshake probing & automatic fallback attempts.

Behavior:
- Probes the WS handshake with header, query-param and subprotocol methods.
- If probe finds a method that completes the handshake, uses it for the persistent connection.
- Preserves writer thread, dry-run, SSL validation, exponential backoff, and CLI overrides.
"""

from __future__ import annotations
import os
import time
import json
import argparse
import logging
import threading
import queue
import random
from datetime import datetime
from infra.sqlite_client import SQLiteClient
from dotenv import load_dotenv
import ssl

# Attempt to import helper libs
try:
    import websocket  # type: ignore
    from websocket import WebSocketException, WebSocketBadStatusException  # type: ignore

    websocket_available = True
except Exception:
    websocket_available = False

# Configure logger early
logger = logging.getLogger("ingestion.dhan_ws")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
if not logger.handlers:
    logger.addHandler(handler)

# Load .env if present
load_dotenv()
logger.info("DHAN WS URL (env): %s", os.getenv("DHAN_WS_URL"))
logger.info(
    "DHAN CLIENT ID (env, masked): %s",
    (
        (os.getenv("DHAN_CLIENT_ID") or "")[:6] + "..."
        if os.getenv("DHAN_CLIENT_ID")
        else None
    ),
)

DB_PATH = "db/ticks.db"
DEFAULT_DHAN_WS_URL = os.getenv("DHAN_WS_URL", "wss://api-feed.dhan.co/v1/live")
DEFAULT_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "")
DEFAULT_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "")

TICK_QUEUE: "queue.Queue[tuple]" = queue.Queue(maxsize=20000)


def _flush_rows_to_db(rows):
    db = SQLiteClient(DB_PATH)
    q = "INSERT OR REPLACE INTO ticks (ts, symbol, price, volume, bid, ask) VALUES (?, ?, ?, ?, ?, ?)"
    for r in rows:
        try:
            db.execute(q, r)
        except Exception:
            logger.exception("DB insert failed for row: %s", r)
    logger.info("Flushed %d ticks to %s", len(rows), DB_PATH)


def writer_worker(batch_size=100, flush_interval=2.0, dry_run=False):
    buffer = []
    last_flush = time.time()
    while True:
        try:
            item = TICK_QUEUE.get(timeout=flush_interval)
        except queue.Empty:
            item = None
        if item is None:
            if buffer and not dry_run:
                _flush_rows_to_db(buffer)
                buffer = []
            continue
        if item == "__STOP__":
            if buffer and not dry_run:
                _flush_rows_to_db(buffer)
            logger.info("Writer worker stopping")
            TICK_QUEUE.task_done()
            break
        if dry_run:
            logger.info("DRY tick: %s", item)
        else:
            buffer.append(item)
        if len(buffer) >= batch_size or (
            (time.time() - last_flush) > flush_interval and buffer
        ):
            if not dry_run:
                _flush_rows_to_db(buffer)
            buffer = []
            last_flush = time.time()
        TICK_QUEUE.task_done()


def parse_msg_to_ticks(msg: dict) -> list[tuple]:
    rows = []
    t = datetime.utcnow().isoformat()
    if not isinstance(msg, dict):
        return rows
    if "data" in msg and isinstance(msg["data"], list):
        for item in msg["data"]:
            sec = item.get("securityId") or item.get("instrument") or item.get("symbol")
            if not sec:
                continue
            symbol = str(sec).split(":")[-1]
            price = item.get("ltp") or item.get("lastTradedPrice") or item.get("price")
            vol = item.get("volume") or item.get("lastTradeQty") or 0
            bid = item.get("bid") or item.get("bestBidPrice")
            ask = item.get("ask") or item.get("bestAskPrice")
            rows.append((t, symbol, price, vol, bid, ask))
        return rows
    sec = msg.get("securityId") or msg.get("instrument") or msg.get("symbol")
    if sec:
        symbol = str(sec).split(":")[-1]
        price = msg.get("ltp") or msg.get("price")
        vol = msg.get("volume") or 0
        bid = msg.get("bid")
        ask = msg.get("ask")
        rows.append((t, symbol, price, vol, bid, ask))
    return rows


def _mask(s: str | None, keep: int = 6):
    if not s:
        return None
    return s[:keep] + "..."


def _validate_clientid(cid: str | None) -> bool:
    if not cid:
        return False
    cid_stripped = cid.strip()
    if (
        not cid_stripped
        or cid_stripped.lower().startswith("your-")
        or cid_stripped.lower() in ("xxx", "none")
    ):
        return False
    if len(cid_stripped) < 4:
        return False
    return True


def handshake_probe_try_create(
    url: str, headers=None, subprotocols=None, sslopt=None, timeout=6
):
    """
    Try a short create_connection handshake and return (success:bool, error_message:str).
    If success returns (True, None). On failure returns (False, repr(error)).
    """
    if not websocket_available:
        return False, "websocket-client not installed"
    try:
        # attempt a short-lived connection to validate handshake
        ws = websocket.create_connection(
            url,
            header=headers,
            subprotocols=subprotocols or [],
            sslopt=sslopt or {"cert_reqs": ssl.CERT_REQUIRED},
            timeout=timeout,
        )
        ws.close()
        return True, None
    except WebSocketBadStatusException as e:
        # contains response info and body in exception message
        return False, f"WebSocketBadStatusException: {e}"
    except WebSocketException as e:
        return False, f"WebSocketException: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def handshake_probe(
    url: str,
    client_id: str,
    access_token: str,
    insecure: bool = False,
    try_alt_headers: bool = False,
):
    """
    Probe multiple handshake methods. Returns dict with keys:
      success: bool
      method: "headers" | "query" | "subprotocol" | "alt-headers" | None
      url: effective URL to use (may include query params)
      headers: headers list used (masked)
      subprotocols: list used (if any)
      last_error: last failure message (for diagnostics)
    """
    sslopt = (
        {"cert_reqs": ssl.CERT_NONE} if insecure else {"cert_reqs": ssl.CERT_REQUIRED}
    )
    base_headers = [
        f"client-id: {client_id}",
        f"access-token: {access_token}",
        "Origin: https://api.dhan.co",
        "User-Agent: qaai-system/1.0",
        "Host: api-feed.dhan.co",
    ]

    # 1) Try normal headers
    ok, err = handshake_probe_try_create(url, headers=base_headers, sslopt=sslopt)
    if ok:
        return {
            "success": True,
            "method": "headers",
            "url": url,
            "headers": base_headers,
            "subprotocols": None,
            "last_error": None,
        }

    last_error = err or "unknown"

    # 2) Try query param approach
    q_url = f"{url}?client_id={client_id}&access_token={access_token}"
    ok, err = handshake_probe_try_create(
        q_url, headers=[("Origin", "https://api.dhan.co")], sslopt=sslopt
    )
    if ok:
        return {
            "success": True,
            "method": "query",
            "url": q_url,
            "headers": None,
            "subprotocols": None,
            "last_error": None,
        }
    last_error = err or last_error

    # 3) Try subprotocol approach
    subproto = f"clientid.{client_id};token.{access_token}"
    ok, err = handshake_probe_try_create(
        url,
        headers=[("Origin", "https://api.dhan.co")],
        subprotocols=[subproto],
        sslopt=sslopt,
    )
    if ok:
        return {
            "success": True,
            "method": "subprotocol",
            "url": url,
            "headers": None,
            "subprotocols": [subproto],
            "last_error": None,
        }
    last_error = err or last_error

    # 4) Try alternate header names (if requested)
    if try_alt_headers:
        alt_keys = [
            ["x-client-id", "x-access-token"],
            ["client_id", "access_token"],
            ["clientid", "accesstoken"],
            ["X-CLIENT-ID", "ACCESS-TOKEN"],
        ]
        for keys in alt_keys:
            hdrs = [
                f"{keys[0]}: {client_id}",
                f"{keys[1]}: {access_token}",
                "Origin: https://api.dhan.co",
                "User-Agent: qaai-system/1.0",
                "Host: api-feed.dhan.co",
            ]
            ok, err = handshake_probe_try_create(url, headers=hdrs, sslopt=sslopt)
            if ok:
                return {
                    "success": True,
                    "method": "alt-headers",
                    "url": url,
                    "headers": hdrs,
                    "subprotocols": None,
                    "last_error": None,
                }
            last_error = err or last_error

    return {
        "success": False,
        "method": None,
        "url": url,
        "headers": None,
        "subprotocols": None,
        "last_error": last_error,
    }


def _sync_ws_run(
    url: str,
    full_syms: list[str],
    client_id: str,
    access_token: str,
    dry_run: bool = False,
    reconnect_backoff=1,
    insecure=False,
    try_alt_headers=False,
):
    if not websocket_available:
        raise RuntimeError(
            "websocket-client not installed; pip install websocket-client"
        )

    # Probe handshake to discover a working method before long-lived connect
    logger.info(
        "Probing handshake methods for %s (insecure=%s, try_alt_headers=%s)",
        url,
        insecure,
        try_alt_headers,
    )
    probe = handshake_probe(
        url, client_id, access_token, insecure=insecure, try_alt_headers=try_alt_headers
    )
    logger.info(
        "Handshake probe result: %s",
        {k: probe[k] for k in ("success", "method", "last_error")},
    )

    if not probe["success"]:
        logger.error(
            "No handshake method succeeded. Last error: %s", probe["last_error"]
        )
        # Fail fast to avoid tight retry loops; leave reconnect/backoff to caller if desired.
        return

    # Prepare final parameters based on probe
    effective_url = probe["url"]
    effective_subprotocols = probe.get("subprotocols")
    headers = probe.get("headers")
    if headers is None:
        # if probe used query or subprotocol, prepare primary headers anyway (masked logs)
        headers = [
            f"client-id: {client_id}",
            "access-token: <masked>",
            "Origin: https://api.dhan.co",
            "User-Agent: qaai-system/1.0",
            "Host: api-feed.dhan.co",
        ]

    logger.info(
        "Using handshake method %s; connecting to %s", probe["method"], effective_url
    )
    logger.info(
        "Final headers (masked if needed): %s",
        [
            h if not h.startswith("access-token:") else "access-token: <masked>"
            for h in (headers or [])
        ],
    )
    if effective_subprotocols:
        logger.info("Using subprotocols: %s", effective_subprotocols)

    def on_message(ws_app, message):
        try:
            parsed = json.loads(message)
        except Exception:
            logger.debug("Non-JSON message received, ignoring")
            return
        ticks = parse_msg_to_ticks(parsed)
        for t in ticks:
            try:
                TICK_QUEUE.put_nowait(t)
            except queue.Full:
                try:
                    _ = TICK_QUEUE.get_nowait()
                except Exception:
                    pass
                try:
                    TICK_QUEUE.put_nowait(t)
                except Exception:
                    pass

    def on_error(ws_app, err):
        logger.warning("WS error: %s", err)

    def on_close(ws_app, code, reason):
        logger.info("WS closed %s %s", code, reason)

    def on_open(ws_app):
        logger.info("WS handshake complete. Sending subscribe payload.")
        try:
            subscribe_payload = {"type": "subscribe", "instruments": full_syms}
            ws_app.send(json.dumps(subscribe_payload))
            logger.info("Subscribe payload sent: %s", subscribe_payload)
        except Exception:
            logger.debug("Failed to send subscribe payload")

    # main reconnect loop
    while True:
        logger.info("Connecting (sync websocket-client) to %s", effective_url)
        ws_app = websocket.WebSocketApp(
            effective_url,
            header=headers,
            subprotocols=effective_subprotocols or [],
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        sslopt = (
            {"cert_reqs": ssl.CERT_NONE}
            if insecure
            else {"cert_reqs": ssl.CERT_REQUIRED}
        )
        try:
            ws_app.run_forever(ping_interval=20, ping_timeout=10, sslopt=sslopt)
            reconnect_backoff = 1
        except Exception as e:
            logger.exception("Sync WS runtime error: %s", e)

        jitter = random.uniform(-0.5, 0.5)
        wait = reconnect_backoff + (0.1 * reconnect_backoff) * jitter
        wait = max(1, min(60, wait))
        logger.warning(
            "WS disconnected; reconnecting in %.1f seconds (backoff=%s)",
            wait,
            reconnect_backoff,
        )
        time.sleep(wait)
        reconnect_backoff = min(60, int(reconnect_backoff * 2))


def run(
    symbols: list[str],
    dry_run: bool = False,
    ws_url: str = None,
    client_id: str = None,
    access_token: str = None,
    insecure=False,
    try_alt_headers=False,
):
    dh_ws = ws_url or DEFAULT_DHAN_WS_URL
    cid = client_id or DEFAULT_CLIENT_ID
    token = access_token or DEFAULT_ACCESS_TOKEN

    logger.info("Runtime DHAN WS URL: %s", dh_ws)
    logger.info("Runtime CLIENT ID (masked): %s", _mask(cid))

    if not _validate_clientid(cid):
        logger.error(
            "Invalid or missing DHAN_CLIENT_ID: %r. Set a valid client id in your .env or pass --client-id.",
            cid,
        )
        return

    if not token or not token.strip():
        logger.error(
            "Missing DHAN_ACCESS_TOKEN. Set DHAN_ACCESS_TOKEN in .env or pass --access-token"
        )
        return

    full_syms = [s if ":" in s else f"NSE_EQ:{s}" for s in symbols]

    writer_thread = threading.Thread(
        target=writer_worker,
        kwargs={"batch_size": 200, "flush_interval": 2.0, "dry_run": dry_run},
        daemon=True,
    )
    writer_thread.start()

    # For Windows prefer sync websocket-client (stable headers)
    try:
        _sync_ws_run(
            dh_ws,
            full_syms,
            client_id=cid,
            access_token=token,
            dry_run=dry_run,
            insecure=insecure,
            try_alt_headers=try_alt_headers,
        )
    except KeyboardInterrupt:
        logger.info("Interrupted by user")

    TICK_QUEUE.put("__STOP__")
    writer_thread.join(timeout=5)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--symbols", "-s", nargs="+", default=[])
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--ws-url", help="Override DHAN_WS_URL at runtime")
    p.add_argument("--client-id", help="Override DHAN_CLIENT_ID at runtime")
    p.add_argument("--access-token", help="Override DHAN_ACCESS_TOKEN at runtime")
    p.add_argument(
        "--insecure", action="store_true", help="Disable cert validation (dev only)"
    )
    p.add_argument(
        "--try-alt-headers",
        action="store_true",
        help="Experimentally try alternate header names",
    )
    args = p.parse_args()
    syms = args.symbols or ["AAPL", "MSFT"]
    run(
        syms,
        dry_run=args.dry_run,
        ws_url=args.ws_url,
        client_id=args.client_id,
        access_token=args.access_token,
        insecure=args.insecure,
        try_alt_headers=args.try_alt_headers,
    )
