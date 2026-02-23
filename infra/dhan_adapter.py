# infra/dhan_adapter.py
"""
Supercharged Dhan adapter + sandbox simulator.

Features:
 - Deterministic sandbox simulation (seedable)
 - Pluggable slippage & fee models
 - Rate limiting with optional queueing/backoff
 - Simple callback hook for notifying orchestrator on fills
 - Adapter wrapper (DhanAdapter) that can wrap either a real client or the sandbox
 - Backwards-compatible aliases: DhanClientSim, BrokerAdapter
"""

from __future__ import annotations
import threading
import time
import uuid
import random
import math
import json
import logging
import os
from typing import Any, Dict, List, Optional, Callable, Tuple
from integrations.dhan_live import DhanLiveConnector
from infra.scheduler import AsyncScheduler

# Optional env config (if present in your repo)
try:
    import qaai_system.env_config as cfg  # prefer package import
except Exception:
    try:
        import env_config as cfg  # fallback
    except Exception:
        cfg = None  # type: ignore

DEFAULT_LOG = logging.getLogger("DhanAdapter")
DEFAULT_LOG.addHandler(logging.NullHandler())

# -------------------------
# Utilities & small helpers
# -------------------------
class RateLimitExceeded(Exception):
    pass


def now_ts() -> float:
    return time.time()


def ensure_list(x):
    return x if isinstance(x, list) else [x]


def register_dhan_feed(scheduler: AsyncScheduler, feed_url, api_key, name="dhan_live"):
    conn = DhanLiveConnector(feed_url=feed_url, api_key=api_key)
    # start as a scheduled job (non-blocking)
    scheduler.start_job(name, conn.start)
    # add stop hook - ensure you call conn.stop() on shutdown
    return conn
    
# -------------------------
# MLFlow / metrics stub (pluggable)
# -------------------------
class MLFlowStub:
    def __init__(self, enabled: bool = False, outpath: str = "mlflow_sandbox.jsonl"):
        self.enabled = bool(enabled)
        self.outpath = outpath

    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        if not self.enabled:
            return
        obj = {"time": now_ts(), "metric": key, "value": value, "step": step}
        with open(self.outpath, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj) + "\n")

    def log_param(self, key: str, value: Any):
        if not self.enabled:
            return
        obj = {"time": now_ts(), "param": key, "value": value}
        with open(self.outpath, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj) + "\n")


# -------------------------
# Slippage / fee models
# -------------------------
def default_slippage(price: float, pct: float, side: str = "BUY") -> float:
    """Small randomized slippage around pct fraction."""
    if price is None:
        return price
    factor = pct * (0.5 + random.random() * 0.5)
    return float(price + factor * price if side.lower() in ("buy", "b") else price - factor * price)


def default_fee(notional: float) -> float:
    """Simple fee model (flat fraction)."""
    return float(abs(notional) * 0.0005)


# -------------------------
# Sandbox simulator
# -------------------------
class DhanAdapterSandbox:
    """
    Full-featured deterministic sandbox simulator.

    Constructor highlights:
      - seed: optional int to make behaviour deterministic (useful in tests)
      - rate_limit_per_sec: throttle; set very large to disable
      - queue_on_rate_limit: if True, calls are queued instead of failing
      - on_fill: optional callback(fn(fill_dict)) that the orchestrator can use to be notified
    """
    def __init__(
        self,
        seed: Optional[int] = None,
        api_key: Optional[str] = None,
        rate_limit_per_sec: float = 200.0,
        queue_on_rate_limit: bool = False,
        enable_mlflow: bool = False,
        slippage_pct: Optional[float] = None,
        default_slippage_pct: Optional[float] = None,  # backward-compatible alias
        fee_model: Callable[[float], float] = default_fee,
        logger: Optional[logging.Logger] = None,
        on_fill: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.logger = logger or DEFAULT_LOG
        self.seed = seed
        self._rand = random.Random(seed)
        self.api_key = api_key or (os.environ.get("DHAN_API_KEY") if os.environ.get("DHAN_API_KEY") else "sandbox-key")
        self.rate_limit_per_sec = float(rate_limit_per_sec or 200.0)
        self.queue_on_rate_limit = bool(queue_on_rate_limit)
        self._lock = threading.RLock()
        self._last_call_ts = 0.0
        self._orders: Dict[str, Dict[str, Any]] = {}
        self._fills: Dict[str, List[Dict[str, Any]]] = {}
        self._positions: Dict[str, Dict[str, Any]] = {}
        self._instruments: Dict[str, Dict[str, Any]] = self._load_default_instruments()
        self.mlflow = MLFlowStub(enabled=enable_mlflow)
        # prefer explicit slippage_pct; fall back to default_slippage_pct for compatibility
        if slippage_pct is None and default_slippage_pct is not None:
            self.slippage_pct = float(default_slippage_pct)
        else:
            self.slippage_pct = float(slippage_pct or 0.0)
        self.fee_model = fee_model
        self._call_count = 0
        self.on_fill = on_fill  # callback
        self._queue: List[Tuple[float, Callable]] = []  # (when, callable)

    def _load_default_instruments(self) -> Dict[str, Dict[str, Any]]:
        # Expand as needed; simple demo set kept small
        return {
            "RELIANCE": {"symbol": "RELIANCE", "exchange": "NSE", "lot": 1, "instrument_type": "EQ"},
            "NIFTY": {"symbol": "NIFTY", "exchange": "NSE", "lot": 1, "instrument_type": "IDX"},
            "BANKNIFTY": {"symbol": "BANKNIFTY", "exchange": "NSE", "lot": 1, "instrument_type": "IDX"},
        }

    # ----------------- Rate limiting -----------------
    def _throttle(self):
        with self._lock:
            if self.rate_limit_per_sec >= 1000:
                self._last_call_ts = now_ts()
                self._call_count += 1
                return
            now = now_ts()
            min_interval = 1.0 / max(1.0, self.rate_limit_per_sec)
            elapsed = now - self._last_call_ts
            if elapsed < min_interval:
                if self.queue_on_rate_limit:
                    # schedule queued call for a tiny delay and return control
                    target = self._last_call_ts + min_interval
                    return ("queued", target)
                raise RateLimitExceeded("Rate limit exceeded")
            self._last_call_ts = now
            self._call_count += 1
            return ("ok", None)

    def ping_broker(self) -> bool:
        self.logger.debug("ping_broker called")
        return True

    def _generate_order_id(self) -> str:
        return str(uuid.uuid4())

    # ----------------- Order lifecycle -----------------
    def submit_order(self, *args, **kwargs) -> str:
        """
        Accepts either a dict as single arg or kwargs.
        Standardizes to keys: order_id, symbol, side, quantity, remaining_qty, price, order_type, product, status, timestamps.
        """
        if args and isinstance(args[0], dict):
            order = dict(args[0])
        else:
            order = dict(kwargs)

        with self._lock:
            r = self._throttle()
            if isinstance(r, tuple) and r[0] == "queued":
                # simple blocking wait until scheduled time
                wait_until = r[1]
                self.logger.debug("submit_order queued until %s", wait_until)
                time.sleep(max(0.0, wait_until - now_ts()))

            # normalize keys
            qty = int(order.get("qty", order.get("quantity", 0)))
            price = None if order.get("price") is None else float(order.get("price"))
            side = str(order.get("side", "BUY")).upper()
            oid = self._generate_order_id()
            ts = now_ts()
            order_rec = {
                "order_id": oid,
                "symbol": order.get("symbol"),
                "side": side,
                "quantity": qty,
                "remaining_qty": qty,
                "price": price,
                "order_type": order.get("order_type", "LMT"),
                "product": order.get("product", "MIS"),
                "status": "OPEN",
                "created_at": ts,
                "updated_at": ts,
            }
            self._orders[oid] = order_rec
            self._fills[oid] = []
            self.mlflow.log_metric("orders_submitted", 1.0, step=self._call_count)
            self.logger.info({"evt": "submit_order", "order": order_rec})
            return oid

    def submit_order_full(self, *a, **k) -> Dict[str, Any]:
        oid = self.submit_order(*a, **k)
        return self.get_order_status(oid) or {"order_id": oid, "status": "UNKNOWN"}

    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            od = self._orders.get(order_id)
            return dict(od) if od else None

    def cancel_order(self, order_id: str) -> bool:
        with self._lock:
            od = self._orders.get(order_id)
            if not od or od["status"] in ("CANCELLED", "FILLED"):
                return False
            od["status"] = "CANCELLED"
            od["updated_at"] = now_ts()
            self.logger.info({"evt": "cancel_order", "order_id": order_id})
            return True

    # ----------------- Fill simulation -----------------
    def simulate_fill(self, order_id: str, price: Optional[float] = None, qty: Optional[int] = None, *, fill_price: Optional[float] = None, filled_qty: Optional[int] = None) -> Dict[str, Any]:
        """
        Simulate a fill for order_id. Accepts both legacy names and newer names:
          - legacy: price=..., qty=...
          - new: fill_price=..., filled_qty=...

        Returns the fill dict.
        """
        # Normalize parameter names (support both signatures)
        if fill_price is None and price is not None:
            fill_price = price
        if filled_qty is None and qty is not None:
            filled_qty = qty

        if fill_price is None or filled_qty is None:
            raise TypeError("simulate_fill requires both price (or fill_price) and qty (or filled_qty)")

        with self._lock:
            od = self._orders.get(order_id)
            if not od:
                raise KeyError("order not found")
            if od["status"] in ("CANCELLED", "FILLED"):
                raise RuntimeError("order not fillable in its current state")

            executed_price = self._apply_slippage(float(fill_price), od["side"])
            fill_qty = int(filled_qty)
            fill_qty = min(fill_qty, od["remaining_qty"])

            fill = {
                "fill_id": str(uuid.uuid4()),
                "order_id": order_id,
                "symbol": od["symbol"],
                "qty": fill_qty,
                "price": float(executed_price),
                "side": od["side"],
                "timestamp": time.time(),
            }
            self._fills.setdefault(order_id, []).append(fill)
            od["remaining_qty"] = max(0, od["remaining_qty"] - fill_qty)
            od["updated_at"] = time.time()
            if od["remaining_qty"] == 0:
                od["status"] = "FILLED"

            pos = self._positions.setdefault(
                od["symbol"],
                {"symbol": od["symbol"], "qty": 0, "avg_price": 0.0, "pnl": 0.0},
            )

            signed_qty = fill_qty if od["side"].lower() in ("buy", "b") else -fill_qty
            prev_qty = pos["qty"]
            prev_avg = pos["avg_price"]

            if prev_qty == 0:
                pos["avg_price"] = fill["price"]
                pos["qty"] = signed_qty
            elif (prev_qty > 0 and signed_qty > 0) or (prev_qty < 0 and signed_qty < 0):
                total_qty = abs(prev_qty) + abs(signed_qty)
                pos["avg_price"] = (
                    abs(prev_qty) * prev_avg + abs(signed_qty) * fill["price"]
                ) / total_qty
                pos["qty"] = prev_qty + signed_qty
            else:
                new_qty = prev_qty + signed_qty
                closed_qty = min(abs(prev_qty), abs(signed_qty))
                if abs(signed_qty) <= abs(prev_qty):
                    if prev_qty > 0:
                        realized = (fill["price"] - prev_avg) * closed_qty
                    else:
                        realized = (prev_avg - fill["price"]) * closed_qty
                    pos["pnl"] = pos.get("pnl", 0.0) + realized
                    pos["qty"] = new_qty
                else:
                    closed_qty = abs(prev_qty)
                    if prev_qty > 0:
                        realized = (fill["price"] - prev_avg) * closed_qty
                    else:
                        realized = (prev_avg - fill["price"]) * closed_qty
                    remaining_qty = new_qty
                    pos["pnl"] = pos.get("pnl", 0.0) + realized
                    pos["qty"] = remaining_qty
                    pos["avg_price"] = fill["price"] if remaining_qty != 0 else 0.0

            # callback hook / mlflow
            try:
                self.mlflow.log_metric("fills", 1.0, step=self._call_count)
            except Exception:
                pass
            # optional on_fill callback
            try:
                if hasattr(self, "on_fill") and callable(self.on_fill):
                    self.on_fill(fill)
            except Exception:
                self.logger.exception("on_fill callback failed")

            return fill

    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {s: dict(p) for s, p in self._positions.items()}

    def get_order_fills(self, order_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._fills.get(order_id, []))

    # inside class DhanAdapterSandbox

    def _apply_slippage(self, price: float, side: str) -> float:
        """
        Apply configured slippage model. Keeps backward compatibility:
        - slippage_pct on the instance (float)
        - a custom slippage function could be supported in future.
        """
        try:
            # Use instance-level function if present (future extension)
            if hasattr(self, "slippage_model") and callable(self.slippage_model):
                return float(self.slippage_model(price, self.slippage_pct, side))
        except Exception:
            # fallback to deterministic default
            pass
        # Use default deterministic slippage based on instance RNG
        # replicate earlier behavior: small randomized factor around self.slippage_pct
        if price is None:
            return price
        factor = self.slippage_pct * (0.5 + self._rand.random() * 0.5)
        return float(price + factor * price if str(side).lower() in ("buy", "b") else price - factor * price)

    # ----------------- Market data -----------------
    def fetch_ohlcv(self, symbol: str, start_ts: float, end_ts: float, timeframe: str = "1m") -> List[Dict[str, Any]]:
        """
        Deterministic-ish OHLCV generator between start_ts and end_ts at timeframe resolution.
        Returns list of dicts {ts, open, high, low, close, volume, source}
        """
        bars: List[Dict[str, Any]] = []
        interval = {"1m": 60, "5m": 300, "1h": 3600, "1d": 86400}.get(timeframe, 60)
        t = int(start_ts - (start_ts % interval))
        while t <= int(end_ts):
            base = 100.0 + math.sin(t / 300.0) * 2.0 + (abs(hash(symbol)) % 10)
            o = base * (0.995 + self._rand.random() * 0.01)
            c = base * (0.995 + self._rand.random() * 0.01)
            h = max(o, c) * (1.0 + self._rand.random() * 0.002)
            l = min(o, c) * (1.0 - self._rand.random() * 0.002)
            v = int(100 + self._rand.random() * 1000)
            bars.append({"ts": t, "open": o, "high": h, "low": l, "close": c, "volume": v, "source": "SANDBOX"})
            t += interval
        if not bars:
            now = int(now_ts())
            base = 100.0 + (abs(hash(symbol)) % 10)
            bars.append({"ts": now, "open": base, "high": base * 1.001, "low": base * 0.999, "close": base, "volume": 100, "source": "SANDBOX"})
        return bars

    # ----------------- Diagnostics -----------------
    def reconcile_with_trade_log(self, trade_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        with self._lock:
            report = {"missing_in_adapter": [], "missing_in_trade_log": [], "mismatched": []}
            adapter_fills = {f["fill_id"]: f for fills in self._fills.values() for f in fills}
            seen = set()
            for entry in trade_log:
                fid = entry.get("fill_id")
                if fid and fid in adapter_fills:
                    seen.add(fid)
                    a = adapter_fills[fid]
                    if abs(a["price"] - entry.get("price", a["price"])) / max(1.0, a["price"]) > 0.02 or a["qty"] != entry.get("qty"):
                        report["mismatched"].append({"adapter": a, "trade_log": entry})
                else:
                    # attempt fuzzy match by order_id + qty + price tolerance
                    matches = [f for f in adapter_fills.values() if f["order_id"] == entry.get("order_id")]
                    if not matches:
                        report["missing_in_adapter"].append(entry)
                    else:
                        matched = False
                        for m in matches:
                            if abs(m["price"] - entry.get("price", m["price"])) / max(1.0, m["price"]) < 0.02 and m["qty"] == entry.get("qty"):
                                seen.add(m["fill_id"])
                                matched = True
                                break
                        if not matched:
                            report["missing_in_adapter"].append(entry)
            for fid, f in adapter_fills.items():
                if fid not in seen:
                    report["missing_in_trade_log"].append(f)
            report["summary"] = {k: len(v) for k, v in report.items() if k != "summary"}
            self.logger.info({"evt": "reconcile", "summary": report["summary"]})
            return report

    def reset(self):
        with self._lock:
            self._orders.clear()
            self._fills.clear()
            self._positions.clear()
            self._last_call_ts = 0.0
            self._call_count = 0

# -------------------------
# Adapter wrapper (unified API)
# -------------------------
class DhanAdapter:
    """
    Thin adapter wrapper that can be constructed with either a real client or the sandbox simulator.

    Example:
        adapter = DhanAdapter(client=some_dhan_client)   # uses real client
        adapter = DhanAdapter(simulator=True, seed=42)    # uses sandbox
    """

    def __init__(self, client: Optional[Any] = None, *, simulator: bool = False, **sim_kwargs):
        if client is not None and simulator:
            raise ValueError("Provide either client OR simulator=True, not both")
        if simulator:
            self.client = DhanAdapterSandbox(**sim_kwargs)
        else:
            if client is None:
                # if your repo exports a DhanClient, prefer it
                try:
                    from infra.dhan_client import DhanClient  # type: ignore
                    client = DhanClient(api_key=os.environ.get("DHAN_API_KEY"))
                except Exception:
                    # no real client found — fall back to sandbox
                    client = DhanAdapterSandbox(**sim_kwargs)
            self.client = client

    # Proxy methods (tolerant to underlying client API)
    def submit_order(self, *args, **kwargs) -> str:
        if hasattr(self.client, "submit_order"):
            return self.client.submit_order(*args, **kwargs)
        if hasattr(self.client, "place_order"):
            return self.client.place_order(*args, **kwargs)
        raise AttributeError("underlying client has no submit_order/place_order")

    def submit_order_full(self, *args, **kwargs) -> Dict[str, Any]:
        if hasattr(self.client, "submit_order_full"):
            return self.client.submit_order_full(*args, **kwargs)
        if hasattr(self.client, "submit_order"):
            oid = self.submit_order(*args, **kwargs)
            if hasattr(self.client, "get_order_status"):
                return self.client.get_order_status(oid) or {"order_id": oid}
            return {"order_id": oid}

    def cancel_order(self, *args, **kwargs) -> bool:
        fn = getattr(self.client, "cancel_order", getattr(self.client, "cancel", None))
        if not fn:
            raise AttributeError("underlying client has no cancel_order/cancel")
        return fn(*args, **kwargs)

    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        fn = getattr(self.client, "get_order_status", getattr(self.client, "get_order", None))
        if not fn:
            return None
        return fn(order_id)

    def get_positions(self) -> Dict[str, Any]:
        if hasattr(self.client, "get_positions"):
            return self.client.get_positions()
        return {}

    def simulate_fill(self, *args, **kwargs):
        if hasattr(self.client, "simulate_fill"):
            return self.client.simulate_fill(*args, **kwargs)
        raise AttributeError("simulate_fill not supported by underlying client")

    def fetch_ohlcv(self, *args, **kwargs):
        if hasattr(self.client, "fetch_ohlcv"):
            return self.client.fetch_ohlcv(*args, **kwargs)
        raise AttributeError("fetch_ohlcv not supported by underlying client")

    def reconcile_with_trade_log(self, *args, **kwargs):
        if hasattr(self.client, "reconcile_with_trade_log"):
            return self.client.reconcile_with_trade_log(*args, **kwargs)
        return {}

    def reset(self):
        if hasattr(self.client, "reset"):
            return self.client.reset()

# Backwards-compatible aliases
DhanClientSim = DhanAdapterSandbox
BrokerAdapter = DhanAdapterSandbox if (not cfg or getattr(cfg, "MODE", "sandbox") != "live") else None

__all__ = ["DhanAdapterSandbox", "DhanAdapter", "DhanClientSim", "BrokerAdapter"]
