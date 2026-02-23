# modules/order/manager.py
"""
OrderManager: idempotent order submission, routing, persistence, retries, partial-fill handling.
Synchronous implementation (requests + sqlite). Designed to be pluggable.
"""
from __future__ import annotations
import sqlite3
import json
import logging
import time
import threading
from typing import Dict, Any, Optional, List, Tuple
import uuid
import math
import requests

logger = logging.getLogger(__name__)


# ----------------------------
# Persistence (SQLite) adapter
# ----------------------------
class SQLiteStore:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        self._init_schema()

    def _init_schema(self):
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                client_order_id TEXT PRIMARY KEY,
                created_at REAL,
                instrument TEXT,
                side TEXT,
                qty REAL,
                price REAL,
                state TEXT,
                payload TEXT,
                exec_endpoint TEXT,
                filled_qty REAL DEFAULT 0,
                avg_price REAL DEFAULT NULL
            )
            """)
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fills (
                id TEXT PRIMARY KEY,
                client_order_id TEXT,
                filled_qty REAL,
                fill_price REAL,
                ts REAL
            )
            """)
            # mapping for client-provided idempotency hints -> coid
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS client_hints (
                hint TEXT PRIMARY KEY,
                client_order_id TEXT
            )
            """)

    def insert_order(self, coid: str, order: Dict[str, Any]):
        with self._lock, self.conn:
            self.conn.execute(
                "INSERT INTO orders (client_order_id, created_at, instrument, side, qty, price, state, payload, exec_endpoint, filled_qty, avg_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (coid, time.time(), order["instrument"], order["side"], float(order["qty"]), float(order.get("price") or 0.0),
                 order.get("state", "NEW"), json.dumps(order), order.get("exec_endpoint"), 0.0, None)
            )

    def update_order_state(self, coid: str, state: str, **kwargs):
        fields = []
        vals = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            vals.append(v)
        fields_sql = ", ".join(fields)
        with self._lock, self.conn:
            if fields_sql:
                self.conn.execute(f"UPDATE orders SET state = ?, {fields_sql} WHERE client_order_id = ?", (state, *vals, coid))
            else:
                self.conn.execute("UPDATE orders SET state = ? WHERE client_order_id = ?", (state, coid))

    def get_order(self, coid: str) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT client_order_id, created_at, instrument, side, qty, price, state, payload, exec_endpoint, filled_qty, avg_price FROM orders WHERE client_order_id = ?", (coid,))
        row = cur.fetchone()
        if not row:
            return None
        keys = ["client_order_id", "created_at", "instrument", "side", "qty", "price", "state", "payload", "exec_endpoint", "filled_qty", "avg_price"]
        obj = dict(zip(keys, row))
        obj["payload"] = json.loads(obj["payload"])
        return obj

    def add_fill(self, coid: str, filled_qty: float, fill_price: float):
        fid = str(uuid.uuid4())
        ts = time.time()
        with self._lock, self.conn:
            self.conn.execute("INSERT INTO fills (id, client_order_id, filled_qty, fill_price, ts) VALUES (?, ?, ?, ?, ?)",
                              (fid, coid, filled_qty, fill_price, ts))
            # update order's filled_qty and avg_price
            cur = self.conn.cursor()
            cur.execute("SELECT filled_qty, avg_price FROM orders WHERE client_order_id = ?", (coid,))
            row = cur.fetchone()
            if not row:
                raise RuntimeError("order not found")
            prev_filled, prev_avg = row
            prev_filled = float(prev_filled or 0.0)
            prev_avg = float(prev_avg) if prev_avg is not None else None
            # compute new average price
            total_qty = prev_filled + filled_qty
            if prev_avg is None:
                new_avg = fill_price
            else:
                new_avg = ((prev_avg * prev_filled) + (fill_price * filled_qty)) / total_qty
            self.conn.execute("UPDATE orders SET filled_qty = ?, avg_price = ? WHERE client_order_id = ?",
                              (total_qty, new_avg, coid))

    def list_open_orders(self) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT client_order_id FROM orders WHERE state NOT IN ('CANCELED', 'FILLED', 'REJECTED')")
        rows = cur.fetchall()
        return [self.get_order(r[0]) for r in rows]

    # ----------------------------
    # client hint helpers
    # ----------------------------
    def get_coid_by_hint(self, hint: str) -> Optional[str]:
        """Return the stored client_order_id for a client-provided hint, or None."""
        cur = self.conn.cursor()
        cur.execute("SELECT client_order_id FROM client_hints WHERE hint = ?", (hint,))
        row = cur.fetchone()
        return row[0] if row else None

    def set_hint(self, hint: str, coid: str):
        """Persist mapping from hint -> coid (INSERT OR REPLACE)."""
        with self._lock, self.conn:
            self.conn.execute("INSERT OR REPLACE INTO client_hints (hint, client_order_id) VALUES (?, ?)", (hint, coid))


# ----------------------------
# Execution Engine (adapter)
# ----------------------------
class ExecutionError(Exception):
    pass


class ExecutionEngineHTTP:
    """
    Example adapter to a broker API.
    Exposes:
      - send_order(coid, order_payload) -> response dict (expecting 'status', 'broker_ord_id' optional)
      - cancel_order(coid, broker_ord_id) -> response dict
    This is a sample; wire your broker's auth/urls here.
    """
    def __init__(self, base_url: str, api_key: Optional[str] = None, session: Optional[requests.Session] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = session or requests.Session()

    def _headers(self):
        h = {"User-Agent": "qaai_system/execution/1.0", "Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def send_order(self, coid: str, payload: Dict[str, Any], timeout: float = 10.0) -> Dict[str, Any]:
        """
        Send order to broker. We include client_order_id in payload so broker can dedupe.
        Handles 429 Retry-After headers and raises ExecutionError on fatal failure.
        """
        url = f"{self.base_url}/orders"
        data = {**payload, "client_order_id": coid}
        attempts = 0
        while attempts < 6:
            attempts += 1
            try:
                r = self.session.post(url, headers=self._headers(), json=data, timeout=timeout)
            except requests.RequestException as e:
                wait = min(60, (2 ** attempts) * 0.2)
                logger.warning("send_order network error, retrying in %.2fs (%s)", wait, e)
                time.sleep(wait)
                continue
            if r.status_code == 429:
                ra = r.headers.get("Retry-After")
                wait = float(ra) if ra and ra.isdigit() else min(60, (2 ** attempts) * 0.5)
                logger.warning("rate limited, sleeping %s", wait)
                time.sleep(wait)
                continue
            if 200 <= r.status_code < 300:
                try:
                    return r.json()
                except Exception:
                    return {"status": "ok", "raw": r.text}
            # 4xx: likely bad request -> don't retry
            if 400 <= r.status_code < 500:
                raise ExecutionError(f"Permanent broker error {r.status_code}: {r.text}")
            # 5xx: retry
            wait = min(60, (2 ** attempts) * 0.5)
            logger.warning("broker 5xx, retrying in %.2fs", wait)
            time.sleep(wait)
        raise ExecutionError("Max attempts sending order")

    def cancel_order(self, coid: str, broker_ord_id: Optional[str] = None, timeout: float = 10.0) -> Dict[str, Any]:
        url = f"{self.base_url}/orders/cancel"
        data = {"client_order_id": coid}
        if broker_ord_id:
            data["broker_order_id"] = broker_ord_id
        attempts = 0
        while attempts < 6:
            attempts += 1
            try:
                r = self.session.post(url, headers=self._headers(), json=data, timeout=timeout)
            except requests.RequestException as e:
                wait = min(60, (2 ** attempts) * 0.2)
                time.sleep(wait)
                continue
            if r.status_code == 429:
                ra = r.headers.get("Retry-After")
                wait = float(ra) if ra and ra.isdigit() else min(60, (2 ** attempts) * 0.5)
                time.sleep(wait)
                continue
            if 200 <= r.status_code < 300:
                try:
                    return r.json()
                except Exception:
                    return {"status": "ok", "raw": r.text}
            if 400 <= r.status_code < 500:
                raise ExecutionError(f"Permanent broker error {r.status_code}: {r.text}")
            wait = min(60, (2 ** attempts) * 0.5)
            time.sleep(wait)
        raise ExecutionError("Max attempts cancelling order")


# ----------------------------
# Router
# ----------------------------
class Router:
    """
    Simple rule-based router that returns a list of candidate execution endpoints.
    Rules example:
      - prefer broker 'A' for instrument starting with 'NSE:'
      - prefer broker 'B' for large qty
    Router returns tuples (engine_instance, tag)
    """
    def __init__(self, candidates: List[Tuple[str, ExecutionEngineHTTP]]):
        # candidates: list of (tag, engine_instance)
        self.candidates = candidates

    def pick(self, instrument: str, qty: float, side: str) -> List[Tuple[str, ExecutionEngineHTTP]]:
        # basic rules: pick all, sorted by a heuristic (for demo select as-is)
        # You can implement weighting, latency scoring, or historical fill-rate
        return self.candidates[:]  # return all as fallback


# ----------------------------
# OrderManager
# ----------------------------
class OrderManager:
    def __init__(self, store: SQLiteStore, router: Router, risk_check_fn=None):
        self.store = store
        self.router = router
        self.risk_check_fn = risk_check_fn or (lambda order: True)
        self._send_lock = threading.Lock()  # avoid duplicate simultaneous sends for same coid

    def _gen_coid(self, base: Optional[str] = None) -> str:
        if base:
            # deterministic-ish
            return f"{base}-{uuid.uuid4().hex[:8]}"
        return str(uuid.uuid4())

    def create_and_send(self, instrument: str, side: str, qty: float, price: Optional[float] = None, client_id_hint: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create order, persist, risk-check, route, and send. Idempotent: if an order with same client_id_hint exists -> reuse.
        Returns the internal order record (from store).
        """
        # Idempotency by client_id_hint: check mapping table first
        if client_id_hint:
            existing_coid = None
            try:
                existing_coid = self.store.get_coid_by_hint(client_id_hint)
            except Exception:
                existing_coid = None
            if existing_coid:
                existing = self.store.get_order(existing_coid)
                if existing:
                    logger.debug("Found existing order for hint %s -> %s", client_id_hint, existing_coid)
                    return existing

        coid = self._gen_coid(client_id_hint)
        payload = {"instrument": instrument, "side": side, "qty": qty, "price": price, "extra": extra, "state": "NEW"}
        # risk check
        if not self.risk_check_fn(payload):
            raise ValueError("Risk checks failed")

        # persist
        self.store.insert_order(coid, {**payload, "state": "NEW", "exec_endpoint": None})

        # save hint mapping if provided (so subsequent calls with same hint are idempotent)
        if client_id_hint:
            try:
                self.store.set_hint(client_id_hint, coid)
            except Exception:
                logger.exception("Failed to persist client hint mapping (non-fatal)")

        # route
        candidates = self.router.pick(instrument, qty, side)
        # try candidates in order until accepted
        last_exc = None
        for tag, engine in candidates:
            try:
                with self._send_lock:
                    # mark as SENT with exec_endpoint candidate
                    self.store.update_order_state(coid, "SENT", exec_endpoint=tag)
                    resp = engine.send_order(coid, payload)
                    # broker accepted or queued
                    # resp expected: {"status":"ok","broker_order_id":"..."} or similar
                    broker_order_id = resp.get("broker_order_id")
                    # mark as ACKED (or keep SENT until ack event)
                    self.store.update_order_state(coid, "ACKED", exec_endpoint=tag)
                    logger.info("Order %s acked by %s -> broker_order_id=%s", coid, tag, broker_order_id)
                    return self.store.get_order(coid)
            except ExecutionError as e:
                logger.warning("Engine %s failed to accept order: %s", tag, e)
                last_exc = e
                # try next candidate
                continue
        # All candidates failed
        self.store.update_order_state(coid, "REJECTED")
        raise RuntimeError(f"All routes failed: last error: {last_exc}")

    def handle_fill_event(self, coid: str, filled_qty: float, fill_price: float):
        """
        Called when a fill/partial-fill arrives (from broker websocket or polling).
        Updates store and performs follow-up actions (risk, notifications).
        """
        logger.info("Handling fill for %s qty=%s price=%s", coid, filled_qty, fill_price)
        self.store.add_fill(coid, float(filled_qty), float(fill_price))
        order = self.store.get_order(coid)
        if not order:
            logger.warning("Fill for unknown order %s", coid)
            return
        filled = float(order.get("filled_qty") or 0.0)
        qty = float(order.get("qty") or 0.0)
        if math.isclose(filled, qty) or filled >= qty:
            logger.info("Order %s filled (total=%s)", coid, filled)
            self.store.update_order_state(coid, "FILLED")
        else:
            self.store.update_order_state(coid, "PART_FILLED")

    def cancel_order(self, coid: str, broker_order_id: Optional[str] = None, promote_retry: bool = True) -> Dict[str, Any]:
        """
        Cancel order idempotently. If already canceled/filled, return state.
        If not, send cancel requests (with retries) to same exec_endpoint or to all endpoints.
        """
        order = self.store.get_order(coid)
        if not order:
            raise KeyError("Unknown order")
        if order["state"] in ("CANCELED", "FILLED", "REJECTED"):
            return order

        exec_endpoint = order.get("exec_endpoint")
        candidates = self.router.candidates if exec_endpoint is None else [(exec_endpoint, self._find_engine_by_tag(exec_endpoint))]

        last_exc = None
        for tag, engine in candidates:
            try:
                resp = engine.cancel_order(coid, broker_order_id=broker_order_id)
                # mark canceled locally
                self.store.update_order_state(coid, "CANCELED")
                logger.info("Order %s canceled via %s", coid, tag)
                return self.store.get_order(coid)
            except ExecutionError as e:
                last_exc = e
                continue
        raise RuntimeError(f"Cancel failed for {coid}: {last_exc}")

    def _find_engine_by_tag(self, tag: str) -> ExecutionEngineHTTP:
        for t, eng in self.router.candidates:
            if t == tag:
                return eng
        raise KeyError("engine not found")

    def reconcile(self):
        """
        Periodic reconciliation: scan open orders and query/exchange to ensure state still accurate.
        Could poll broker / use websocket snapshots. For demo, this just logs.
        """
        open_orders = self.store.list_open_orders()
        logger.info("Reconciling %d open orders", len(open_orders))
        for o in open_orders:
            logger.debug("Open order: %s state=%s filled=%s/%s", o["client_order_id"], o["state"], o["filled_qty"], o["payload"].get("qty"))


# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    store = SQLiteStore(path=":memory:")
    # two fake endpoints (for demo they point to same base; in real use different brokers)
    eng_a = ExecutionEngineHTTP("https://api.mockbrokerA.test")
    eng_b = ExecutionEngineHTTP("https://api.mockbrokerB.test")
    router = Router(candidates=[("A", eng_a), ("B", eng_b)])
    om = OrderManager(store, router)

    # Create and send an order (this will attempt A then B)
    try:
        rec = om.create_and_send("NSE:RELIANCE", "BUY", 10, price=2500.0)
        print("created:", rec)
    except Exception as e:
        print("submit failed", e)
