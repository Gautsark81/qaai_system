# Path: src/feeds/dhan_v2_feed.py
"""
Dhan v2 Live Market Feed client (async) — with binary parsing & chunked subscription.

Features:
- Builds WS url from token/clientId if needed (uses src.config.config.selected_ws_url)
- Subscribes instruments in batches of <= SUBSCRIBE_BATCH_SIZE (docs: 100)
- Parses binary response header (8 bytes, little-endian) and common payloads:
    - Ticker Packet (Response Header code = 2)
    - Quote Packet (Response Header code = 4)
    - Full Packet (Response Header code = 8) — parsed partially (LTP, qty, time, depth omitted)
    - Disconnect Packet (Response Header code = 50) -> reads disconnection code (int16) and logs
- Emits normalized dict events: {"source":"dhan_v2","received_at":..., "feed_code":int, "exchange_segment":..., "security_id":..., "payload":{...}, "raw": bytes}
- Handles HTTP 429 (InvalidStatus) with escalating backoff & pause
- Handles ConnectionClosedError and other exceptions gracefully
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import random
import struct
from typing import Callable, Optional, Dict, Any, List

from src.config import config
import websockets
from websockets.exceptions import ConnectionClosedError, InvalidStatus

logger = logging.getLogger("src.feeds.dhan_v2_feed")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)


# Response header layout (little-endian)
# Byte 0: feed response code (uint8)
# Bytes 1-2: message length (int16)
# Byte 3: exchange segment (uint8)
# Bytes 4-7: security id (int32)
_HEADER_STRUCT = "<B H B I"  # uint8, uint16, uint8, uint32  (little-endian)
_HEADER_LEN = struct.calcsize(_HEADER_STRUCT)  # should be 1+2+1+4 = 8


def _parse_header(b: bytes):
    if len(b) < _HEADER_LEN:
        raise ValueError("header too short")
    feed_code, msg_len, exch_seg, sec_id = struct.unpack(_HEADER_STRUCT, b[:_HEADER_LEN])
    return int(feed_code), int(msg_len), int(exch_seg), int(sec_id)


def _read_float32_le(b: bytes, offset: int):
    return struct.unpack_from("<f", b, offset)[0]


def _read_int32_le(b: bytes, offset: int):
    return struct.unpack_from("<i", b, offset)[0]


def _read_int16_le(b: bytes, offset: int):
    return struct.unpack_from("<h", b, offset)[0]


class DhanV2Feed:
    def __init__(
        self,
        token: str,
        client_id: str,
        request_instruments: Optional[List[Dict[str, str]]] = None,
        endpoint: str = "wss://api-feed.dhan.co",
        on_message: Optional[Callable[[Dict[str, Any]], None]] = None,
        version: str = "2",
        auth_type: int = 2,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        reconnect_max_backoff: int = 300,
        origin: Optional[str] = None,
        max_429_attempts: int = 5,
    ):
        self.token = token
        self.client_id = client_id
        self.endpoint = endpoint.rstrip("/")
        self.version = version
        self.auth_type = auth_type
        self.request_instruments = request_instruments or []
        self._on_message = on_message
        self._loop = loop or asyncio.new_event_loop()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._reconnect_max_backoff = reconnect_max_backoff
        self.origin = origin or "https://api.dhan.co"
        self._consecutive_429 = 0
        self.max_429_attempts = max_429_attempts

        # derived bounds from config
        self._subscribe_batch_size = config.SUBSCRIBE_BATCH_SIZE
        self._max_instruments_per_conn = config.MAX_INSTRUMENTS_PER_CONNECTION

    def build_url(self) -> str:
        return f"{self.endpoint}?version={self.version}&token={self.token}&clientId={self.client_id}&authType={self.auth_type}"

    def _chunk_instruments(self, instruments: List[Dict[str, str]]) -> List[List[Dict[str, str]]]:
        # ensure instruments count per connection <= max allowed (docs: 5000)
        if len(instruments) > self._max_instruments_per_conn:
            logger.warning("Instruments list length (%d) exceeds max per connection (%d). Truncating to first %d instruments.",
                           len(instruments), self._max_instruments_per_conn, self._max_instruments_per_conn)
            instruments = instruments[: self._max_instruments_per_conn]
        batches = []
        for i in range(0, len(instruments), self._subscribe_batch_size):
            batches.append(instruments[i : i + self._subscribe_batch_size])
        return batches

    def _build_subscribe_message(self, instruments_batch: List[Dict[str, str]]) -> str:
        payload = {
            "RequestCode": 15,
            "InstrumentCount": len(instruments_batch),
            "InstrumentList": instruments_batch,
        }
        return json.dumps(payload)

    async def _sleep_backoff(self, backoff: float):
        jitter = random.uniform(0.5, 1.5)
        delay = min(self._reconnect_max_backoff, backoff) + jitter
        logger.info("Sleeping for %.1fs (backoff + jitter)", delay)
        await asyncio.sleep(delay)

    def _emit(self, event: Dict[str, Any]):
        try:
            if self._on_message:
                self._on_message(event)
        except Exception:
            logger.exception("on_message handler raised an exception")

    def _parse_binary_message(self, b: bytes) -> Dict[str, Any]:
        # parse header
        if len(b) < _HEADER_LEN:
            return {"error": "frame-too-short", "raw": b}
        try:
            feed_code, msg_len, exch_seg, sec_id = _parse_header(b[:_HEADER_LEN])
        except Exception as ex:
            return {"error": f"header-parse-failed:{ex}", "raw": b}

        payload_bytes = b[_HEADER_LEN : _HEADER_LEN + msg_len] if len(b) >= _HEADER_LEN + msg_len else b[_HEADER_LEN:]
        parsed_payload: Dict[str, Any] = {"raw_payload_bytes_len": len(payload_bytes)}

        # feed_code meanings per docs: Ticker=2, Quote=4, OI=5, PrevClose=6, Full=8, Disconnect=50 etc.
        if feed_code == 2:  # Ticker: LTP (float32) + LTT (int32)
            if len(payload_bytes) >= 8:
                ltp = _read_float32_le(payload_bytes, 0)
                ltt = _read_int32_le(payload_bytes, 4)
                parsed_payload.update({"ltp": float(ltp), "ltt_epoch": int(ltt)})
            else:
                parsed_payload.update({"error": "ticker-payload-too-short", "payload_len": len(payload_bytes)})
        elif feed_code == 4:  # Quote Packet
            # as per doc: offsets (relative to payload start)
            # 0-3 float32 LTP, 4-5 int16 last traded qty, 6-9 int32 LTT, 10-13 float32 ATP, 14-17 int32 Volume, ...
            try:
                # ensure at least 18 bytes available for basic fields
                if len(payload_bytes) >= 18:
                    ltp = _read_float32_le(payload_bytes, 0)
                    ltq = _read_int16_le(payload_bytes, 4)
                    ltt = _read_int32_le(payload_bytes, 6)
                    atp = _read_float32_le(payload_bytes, 10)
                    vol = _read_int32_le(payload_bytes, 14)
                    parsed_payload.update(
                        {
                            "ltp": float(ltp),
                            "last_traded_qty": int(ltq),
                            "ltt_epoch": int(ltt),
                            "atp": float(atp),
                            "volume": int(vol),
                        }
                    )
                else:
                    parsed_payload.update({"error": "quote-payload-too-short", "payload_len": len(payload_bytes)})
            except Exception as ex:
                parsed_payload.update({"error": f"quote-parse-exception:{ex}"})
        elif feed_code == 8:  # Full Packet (partial parse - LTP, qty, time, depth exists but depth parsing is longer)
            try:
                if len(payload_bytes) >= 18:
                    ltp = _read_float32_le(payload_bytes, 0)
                    ltq = _read_int16_le(payload_bytes, 4)
                    ltt = _read_int32_le(payload_bytes, 6)
                    atp = _read_float32_le(payload_bytes, 10)
                    vol = _read_int32_le(payload_bytes, 14)
                    parsed_payload.update({"ltp": float(ltp), "last_traded_qty": int(ltq), "ltt_epoch": int(ltt), "atp": float(atp), "volume": int(vol)})
                else:
                    parsed_payload.update({"error": "full-payload-too-short", "payload_len": len(payload_bytes)})
            except Exception as ex:
                parsed_payload.update({"error": f"full-parse-exception:{ex}"})
        elif feed_code == 50:  # Disconnect packet (per docs)
            # docs: header code 50, then 9-10 int16 = disconnection message code
            try:
                if len(payload_bytes) >= 2:
                    disconnect_code = _read_int16_le(payload_bytes, 0)
                    parsed_payload.update({"disconnect_code": int(disconnect_code)})
                else:
                    parsed_payload.update({"error": "disconnect-payload-too-short", "payload_len": len(payload_bytes)})
            except Exception as ex:
                parsed_payload.update({"error": f"disconnect-parse-exception:{ex}"})
        else:
            # unknown code: keep raw payload length and hex preview
            parsed_payload.update({"note": "unknown-feed-code", "code": int(feed_code), "payload_len": len(payload_bytes)})

        event = {
            "source": "dhan_v2",
            "received_at": time.time(),
            "feed_code": int(feed_code),
            "message_length": int(msg_len),
            "exchange_segment": int(exch_seg),
            "security_id": int(sec_id),
            "payload": parsed_payload,
            "raw": b,  # raw bytes for advanced decoding / auditing
        }
        return event

    async def _connect_and_listen(self):
        url = self.build_url()
        backoff = 1.0
        max_size = 2 ** 20 * 10  # 10 MB
        while self._running:
            try:
                logger.info("Connecting to Dhan v2 feed: %s", url)
                # minimal headers to avoid create_connection signature problems
                extra_headers = [("User-Agent", "qaai_system/1.0")]
                async with websockets.connect(
                    url,
                    ping_interval=10,  # server pings every 10s per docs
                    ping_timeout=30,  # allow 30s for pong
                    max_queue=64,
                    max_size=max_size,
                    close_timeout=5,
                    extra_headers=extra_headers,
                ) as ws:
                    logger.info("WebSocket connected; sending subscription batches (batch_size=%d)", self._subscribe_batch_size)
                    # Send subscription messages in chunks of <= SUBSCRIBE_BATCH_SIZE
                    batches = self._chunk_instruments(self.request_instruments)
                    for b in batches:
                        msg = self._build_subscribe_message(b)
                        logger.info("Sending subscribe message with %d instruments", len(b))
                        try:
                            await ws.send(msg)
                        except ConnectionClosedError as cce:
                            logger.error("Connection closed while sending subscribe: %s", cce)
                            raise
                        # slight delay between subscribe messages to be polite
                        await asyncio.sleep(0.1)

                    # reset consecutive 429 counter on successful connect
                    if self._consecutive_429:
                        logger.info("Successful connect: resetting consecutive 429 counter (was=%d)", self._consecutive_429)
                        self._consecutive_429 = 0

                    backoff = 1.0
                    # now handle binary frames (server sends binary responses)
                    async for raw in ws:
                        if raw is None:
                            continue
                        # raw is either str or bytes; docs say responses are binary
                        if isinstance(raw, bytes):
                            try:
                                event = self._parse_binary_message(raw)
                                self._emit(event)
                            except Exception as ex:
                                logger.exception("Failed to parse binary message: %s", ex)
                                # still emit minimal raw event
                                self._emit({"source": "dhan_v2", "received_at": time.time(), "raw": raw, "error": str(ex)})
                        else:
                            # text frames — may be info or debug; try to parse JSON
                            try:
                                txt = json.loads(raw)
                            except Exception:
                                txt = {"raw_text": raw}
                            self._emit({"source": "dhan_v2", "received_at": time.time(), "payload_text": txt})
            except InvalidStatus as isc:
                text = str(isc)
                logger.error("InvalidStatus during websocket connect: %s", text)
                if "429" in text:
                    self._consecutive_429 += 1
                    logger.warning("Received HTTP 429 from server (consecutive=%d)", self._consecutive_429)
                    if self._consecutive_429 >= self.max_429_attempts:
                        long_pause = min(3600, backoff * 20)
                        logger.error("Too many 429s — pausing for %.0fs before next attempt. Check token/account/whitelisting.", long_pause)
                        await asyncio.sleep(long_pause)
                        self._consecutive_429 = 0
                        backoff = 1.0
                    else:
                        await self._sleep_backoff(backoff * 2)
                        backoff = min(self._reconnect_max_backoff, backoff * 2)
                else:
                    logger.error("Invalid status: %s", text)
                    await self._sleep_backoff(backoff * 2)
                    backoff = min(self._reconnect_max_backoff, backoff * 2)
                continue
            except ConnectionClosedError as cce:
                code = getattr(cce, "code", None)
                reason = getattr(cce, "reason", None)
                logger.error("Feed connection closed by server (code=%s reason=%s): %s", code, reason, cce)
                # if server closes with application-level code (e.g., 805 for >5 sockets) log & escalate
                await self._sleep_backoff(backoff)
                backoff = min(self._reconnect_max_backoff, backoff * 2)
                continue
            except Exception as ex:
                logger.exception("Feed connection error: %s", ex)
                await self._sleep_backoff(backoff)
                backoff = min(self._reconnect_max_backoff, backoff * 2)
                logger.info("Reconnecting after backoff=%s", backoff)
                continue

    def start_background(self):
        if self._running:
            logger.warning("DhanV2Feed already running")
            return
        self._running = True

        def _run_loop(loop: asyncio.AbstractEventLoop):
            asyncio.set_event_loop(loop)
            self._task = loop.create_task(self._connect_and_listen())
            try:
                loop.run_forever()
            finally:
                if self._task and not self._task.done():
                    self._task.cancel()
                pending = asyncio.all_tasks(loop=loop)
                for t in pending:
                    t.cancel()
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()

        import threading

        th = threading.Thread(target=_run_loop, args=(self._loop,), name="dhan-v2-feed", daemon=True)
        th.start()
        logger.info("DhanV2Feed background thread started")

    def stop(self):
        if not self._running:
            return
        self._running = False
        try:
            if self._loop.is_running():
                self._loop.call_soon_threadsafe(self._loop.stop)
        except Exception:
            logger.exception("Error stopping loop")

    def run_forever(self):
        self._running = True
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect_and_listen())
