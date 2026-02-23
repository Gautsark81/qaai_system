# modules/dhan/fetcher.py
"""
DhanFetcher with enhanced subscribe-ACK handling, retry/backoff, and improved
ack->subscription matching.

Backwards compatible: defaults keep previous behavior (await_subscribe_ack=False).
"""

from __future__ import annotations
import asyncio
import json
import logging
import sqlite3
import time
from typing import Optional, Callable, Dict, Any

from modules.dhan.ws_provider import WsProvider

logger = logging.getLogger(__name__)

InboundHandler = Callable[[Dict[str, Any]], "asyncio.Future[None]"]
SubscriptionKeyResolver = Callable[[Dict[str, Any], Dict[str, Dict[str, Any]]], Optional[str]]
# resolver(payload, subscriptions) -> subkey or None


class SeqStore:
    """SQLite-backed store for last-seen sequence numbers per subscription key."""
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._init_schema()
        self._lock = asyncio.Lock()

    def _init_schema(self):
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS seqs (
                subkey TEXT PRIMARY KEY,
                last_seq INTEGER
            )
            """)

    def get_last_seq(self, subkey: str) -> Optional[int]:
        cur = self.conn.cursor()
        cur.execute("SELECT last_seq FROM seqs WHERE subkey = ?", (subkey,))
        row = cur.fetchone()
        return int(row[0]) if row else None

    def set_last_seq(self, subkey: str, seq: int):
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO seqs (subkey, last_seq) VALUES (?, ?)",
                (subkey, int(seq)),
            )


class DhanFetcher:
    def __init__(
        self,
        ws_url: str,
        seq_store: SeqStore,
        inbound_handler: Optional[InboundHandler] = None,
        auth_payload: Optional[Dict[str, Any]] = None,
        ping_interval: float = 20.0,
        *,
        # ACK behaviour (all optional; defaults preserve previous behaviour)
        await_subscribe_ack: bool = False,
        subscribe_ack_timeout: float = 1.0,
        subscribe_ack_retries: int = 2,
        subscribe_ack_backoff: float = 0.2,
        # optional resolver to map an ack payload -> subkey (payload, subscriptions) -> subkey
        subscription_key_resolver: Optional[SubscriptionKeyResolver] = None,
    ):
        """
        - await_subscribe_ack: if True, wait for a "subscribed" ack before accepting ticks
        - subscribe_ack_timeout: seconds to wait per attempt
        - subscribe_ack_retries: number of retries (total attempts = retries + 1)
        - subscribe_ack_backoff: base backoff time between attempts (multiplied by attempt index)
        - subscription_key_resolver: optional callable(payload, subscriptions) -> subkey
            useful to integrate external lookups (e.g., DhanHQ API) or custom matching.
        """
        self.seq_store = seq_store
        self.inbound_handler = inbound_handler or (lambda msg: asyncio.create_task(self._noop(msg)))

        self.ws = WsProvider(
            ws_url,
            inbound_cb=self._on_message,
            auth_payload=auth_payload,
            ping_interval=ping_interval,
        )

        self._running = False
        # mapping of subkey -> user subscription payload (resend on reconnect)
        self._subscriptions: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

        # ACK config + state
        self.await_subscribe_ack = await_subscribe_ack
        self.subscribe_ack_timeout = float(subscribe_ack_timeout)
        self.subscribe_ack_retries = int(subscribe_ack_retries)
        self.subscribe_ack_backoff = float(subscribe_ack_backoff)
        self.subscription_key_resolver = subscription_key_resolver

        self._pending_acks: Dict[str, asyncio.Future] = {}   # subkey -> Future
        self._ack_received: Dict[str, bool] = {}            # subkey -> bool

    async def _noop(self, msg):
        return None

    async def start(self):
        if self._running:
            return
        await self.ws.start()
        self._running = True

        # re-send subscriptions (and wait for ack if configured)
        async with self._lock:
            for key, payload in self._subscriptions.items():
                await self._subscribe_internal(key, payload)

        logger.info("DhanFetcher started")

    async def stop(self):
        if not self._running:
            return
        await self.ws.stop()
        self._running = False
        logger.info("DhanFetcher stopped")

    # -------------------------------
    # SUBSCRIBE LOGIC + ACK HANDLING
    # -------------------------------

    async def subscribe(self, subkey: str, payload: Dict[str, Any]):
        """
        Register subscription and ask underlying provider to send it.
        subkey: stable key for resume/dedup (e.g. "tick:RELIANCE")
        payload: JSON-serializable subscribe message to send
        """
        async with self._lock:
            last_seq = self.seq_store.get_last_seq(subkey)
            if last_seq is not None:
                payload = {**payload, "resume_seq": last_seq}
            self._subscriptions[subkey] = payload
            await self._subscribe_internal(subkey, payload)

    async def _subscribe_internal(self, subkey: str, payload: Dict[str, Any]):
        """
        Send subscribe and optionally wait for ACK with retries/backoff.
        """
        await self.ws.subscribe(subkey, payload)

        # reset ack state for this subkey
        self._ack_received[subkey] = False

        if not self.await_subscribe_ack:
            return

        # create future to be resolved on ack
        loop = asyncio.get_event_loop()
        fut = loop.create_future()
        self._pending_acks[subkey] = fut

        attempts = 0
        while attempts <= self.subscribe_ack_retries:
            attempts += 1
            try:
                logger.debug("Waiting for subscribe ACK for %s (attempt %d/%d)", subkey, attempts, self.subscribe_ack_retries + 1)
                # Protect the future from external cancellation; prevents CancelledError bubbling up.
                await asyncio.wait_for(asyncio.shield(fut), timeout=self.subscribe_ack_timeout)
                # ack received
                self._ack_received[subkey] = True
                logger.info("Subscribe ACK received for %s", subkey)
                break
            except asyncio.TimeoutError:
                if attempts > self.subscribe_ack_retries:
                    logger.warning("Subscribe ACK not received for %s after %d attempts; continuing", subkey, attempts - 1)
                    break
                backoff = self.subscribe_ack_backoff * attempts
                logger.debug("Subscribe ACK timeout for %s; retrying after %.3fs", subkey, backoff)
                await asyncio.sleep(backoff)
                # resend subscribe on retry (best-effort)
                try:
                    await self.ws.subscribe(subkey, payload)
                except Exception:
                    logger.exception("Failed to re-send subscribe for %s", subkey)
                    # continue loop; fut still waiting
            except asyncio.CancelledError:
                # The surrounding task was cancelled (e.g., shutdown). Treat like timeout and continue cleanup.
                logger.debug("Subscribe wait cancelled for %s; treating as timeout", subkey)
                break

        # cleanup pending future if still present
        self._pending_acks.pop(subkey, None)

    # -------------------------------
    # MESSAGE HANDLING
    # -------------------------------

    async def _on_message(self, msg: Dict[str, Any]):
        """
        Incoming message handler from WsProvider.
        - recognizes 'subscribed' acks and resolves waiting futures
        - ignores tick messages for subscriptions that haven't received ACK yet (if enabled)
        """
        try:
            mtype = msg.get("type")

            # SUBSCRIBE ACK handling
            if mtype == "subscribed":
                await self._handle_subscribe_ack(msg)
                return

            # Non-tick messages forwarded
            if mtype != "tick":
                await self._maybe_handle_control(msg)
                return

            # Tick handling
            symbol = msg.get("symbol") or msg.get("s") or msg.get("instrument")
            if symbol is None:
                await self._dispatch(msg)
                return

            subkey = f"tick:{symbol}"

            # If we are awaiting ACK for this subkey, drop ticks until ack received
            if self.await_subscribe_ack and not self._ack_received.get(subkey, False):
                logger.debug("Dropping tick for %s because ACK not yet received", subkey)
                return

            seq = msg.get("seq")
            if seq is None:
                await self._dispatch(msg)
                return

            last = self.seq_store.get_last_seq(subkey)
            if last is not None and int(seq) <= int(last):
                logger.debug("Ignoring duplicate/old message for %s seq=%s <= last=%s", subkey, seq, last)
                return

            self.seq_store.set_last_seq(subkey, int(seq))
            await self._dispatch(msg)

        except Exception:
            logger.exception("Error in DhanFetcher._on_message")

    async def _handle_subscribe_ack(self, msg: Dict[str, Any]):
        """
        Resolve pending ACK futures by matching ack payload to a subscription key.
        Matching strategies:
          - If a custom subscription_key_resolver is provided, use it first.
          - Otherwise attempt: exact "symbol" -> tick:<symbol>, then try matching by
            channel+symbol or instrument fields, and finally search registered subscriptions
            for any overlapping keys/fields.
        Once matched, mark ack received and resolve any pending future.
        """
        payload = msg.get("payload", {}) or {}
        # prefer explicit symbol
        symbol = payload.get("symbol") or payload.get("s") or payload.get("instrument")
        channel = payload.get("channel")

        # 1) custom resolver hook
        subkey = None
        if self.subscription_key_resolver:
            try:
                subkey = self.subscription_key_resolver(payload, self._subscriptions)
            except Exception:
                logger.exception("subscription_key_resolver failed")

        # 2) conventional resolution: tick:<symbol>
        if subkey is None and symbol:
            cand = f"tick:{symbol}"
            if cand in self._subscriptions:
                subkey = cand

        # 3) combined (channel+symbol) resolution
        if subkey is None and channel and symbol:
            # e.g. some providers may use "<channel>:<symbol>" style keys; check exact or candidates
            cand1 = f"{channel}:{symbol}"
            if cand1 in self._subscriptions:
                subkey = cand1
            else:
                # also check "tick:SYMBOL" variant
                cand2 = f"tick:{symbol}"
                if cand2 in self._subscriptions:
                    subkey = cand2

        # 4) fallback: search subscriptions for a payload-match (best-effort)
        if subkey is None:
            for registered_key, reg_payload in self._subscriptions.items():
                # compare keys present in ack payload against reg_payload; if symbol or instrument match, consider matched
                if symbol and (reg_payload.get("symbol") == symbol or reg_payload.get("s") == symbol or reg_payload.get("instrument") == symbol):
                    subkey = registered_key
                    break
                if channel and reg_payload.get("channel") == channel:
                    subkey = registered_key
                    break

        if subkey:
            # mark as acknowledged
            self._ack_received[subkey] = True
            fut = self._pending_acks.get(subkey)
            if fut and not fut.done():
                try:
                    fut.set_result(True)
                except Exception:
                    logger.exception("Failed to set ACK future result for %s", subkey)

        # forward ack to inbound_handler as well
        await self._dispatch(msg)

    async def unsubscribe(self, subkey: str, payload: Optional[Dict[str, Any]] = None):
        async with self._lock:
            self._subscriptions.pop(subkey, None)
            # clear ack state
            self._pending_acks.pop(subkey, None)
            self._ack_received.pop(subkey, None)
            await self.ws.unsubscribe(subkey, payload)

    async def _maybe_handle_control(self, msg: Dict[str, Any]):
        await self._dispatch(msg)

    async def _dispatch(self, msg: Dict[str, Any]):
        try:
            await self.inbound_handler(msg)
        except Exception:
            logger.exception("inbound_handler error")
