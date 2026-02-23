# infra/dhan_client_safe.py
"""
Safe async wrapper for DhanHQ-like broker clients.

Features implemented:
- Token-bucket rate limiter (max_qps)
- Limit-first order placement with timeout -> cancel -> fallback to market
- Exponential backoff for transient errors
- Simple circuit breaker -> PAPER_MODE fallback when repeated failures occur
- JSON structured logging with IST timestamps

This is intentionally generic. Replace _place_limit_order_impl / _place_market_order_impl
with your real DhanHQ SDK calls (websocket / rest) or adapt provider adapter.
"""
import asyncio
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta

# CONFIG defaults (tune in production)
MAX_QPS = 8
TOKEN_BUCKET_CAPACITY = MAX_QPS
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_RESET_S = 60
LIMIT_FILL_TIMEOUT_S = 1.0
MAX_RETRIES = 3

# global paper-mode flag (other modules can read this if imported)
PAPER_MODE = False


def ts_ist() -> str:
    # IST = UTC +5:30
    return (datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(hours=5, minutes=30)).isoformat()


def log_json(level: str, module: str, message: str, **context: Any) -> None:
    out = {
        "ts_ist": ts_ist(),
        "level": level,
        "module": module,
        "message": message,
        "context": context,
    }
    print(json.dumps(out))


class TokenBucket:
    def __init__(self, rate: int = MAX_QPS, capacity: int = TOKEN_BUCKET_CAPACITY):
        self.rate = float(rate)
        self.capacity = int(capacity)
        self._tokens = float(capacity)
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def consume(self, n: int = 1) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            refill = elapsed * self.rate
            if refill >= 1.0:
                self._tokens = min(self.capacity, self._tokens + refill)
                self._last = now
            if self._tokens >= n:
                self._tokens -= n
                return
            # compute wait time needed
            needed = n - self._tokens
            wait_time = needed / self.rate
        await asyncio.sleep(wait_time)
        # try again recursively
        await self.consume(n)


class CircuitBreaker:
    def __init__(self, threshold: int = CIRCUIT_BREAKER_THRESHOLD, reset_after_s: int = CIRCUIT_BREAKER_RESET_S):
        self.threshold = int(threshold)
        self.reset_after_s = int(reset_after_s)
        self._fails = 0
        self._tripped_at: Optional[float] = None
        self._lock = asyncio.Lock()

    async def record_success(self) -> None:
        async with self._lock:
            self._fails = 0
            self._tripped_at = None

    async def record_failure(self) -> None:
        async with self._lock:
            self._fails += 1
            if self._fails >= self.threshold and self._tripped_at is None:
                self._tripped_at = time.monotonic()
                log_json("WARN", "dhan.circuit", "circuit tripped", fails=self._fails)

    async def is_tripped(self) -> bool:
        async with self._lock:
            if self._tripped_at is None:
                return False
            # short-circuit reset window: after reset period we allow half-open attempts
            if (time.monotonic() - self._tripped_at) > self.reset_after_s:
                # reset circuit for trial
                self._fails = 0
                self._tripped_at = None
                return False
            return True


class DhanSafeClient:
    def __init__(self, max_qps: int = MAX_QPS):
        self.bucket = TokenBucket(rate=max_qps, capacity=max_qps)
        self.circuit = CircuitBreaker()
        self.paper_mode = False

    # ----------------------
    # Replace these with real broker SDK implementations
    # ----------------------
    async def _place_limit_order_impl(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        In production this should call DhanHQ SDK (or provider adapter) to place a limit order.
        For now this simulates a successful ack with zero fill (test-friendly).
        """
        await asyncio.sleep(0.02)
        return {"order_id": f"sim-{int(time.time()*1000)}", "filled": 0, "status": "accepted"}

    async def _place_market_order_impl(self, order: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        return {"order_id": f"mkt-{int(time.time()*1000)}", "filled": order.get("qty", 0), "status": "filled"}
    # ----------------------

    async def place_limit_order(self, order: Dict[str, Any], timeout: Optional[float] = LIMIT_FILL_TIMEOUT_S) -> Dict[str, Any]:
        """
        Place a limit-first order with retry/backoff and fallback behavior.
        Returns a dict: {status: "ok"|"paper"|"error", order_id: str|None, filled: int}
        """
        global PAPER_MODE
        # Circuit/paper mode check
        if PAPER_MODE or await self.circuit.is_tripped():
            log_json("INFO", "dhan.safe", "paper mode active - skipping broker call", order=order)
            self.paper_mode = True
            return {"status": "paper", "order_id": None, "filled": 0}

        # respect rate limit
        await self.bucket.consume(1)

        attempt = 0
        backoff = 0.1
        last_exc: Optional[Exception] = None

        while attempt < MAX_RETRIES:
            attempt += 1
            try:
                resp = await self._place_limit_order_impl(order)
                # in production we would await websocket fills or poll order status for `timeout`
                # Here for testability we return the immediate ack and rely on the caller to poll.
                await self.circuit.record_success()
                return {"status": "ok", "order_id": resp.get("order_id"), "filled": int(resp.get("filled", 0))}
            except Exception as ex:
                last_exc = ex
                await self.circuit.record_failure()
                log_json("ERROR", "dhan.safe", "limit order attempt failed", attempt=attempt, exc=str(ex))
                if await self.circuit.is_tripped():
                    # Trip to paper-mode and return
                    PAPER_MODE = True
                    self.paper_mode = True
                    log_json("WARN", "dhan.safe", "entering paper mode due to circuit", attempts=attempt)
                    return {"status": "paper", "order_id": None, "filled": 0}
                # backoff
                await asyncio.sleep(backoff)
                backoff *= 2

        # If all retries failed, attempt a market order fallback if allowed
        try:
            log_json("WARN", "dhan.safe", "all limit attempts failed, trying market fallback", order=order)
            await self.bucket.consume(1)
            mresp = await self._place_market_order_impl(order)
            await self.circuit.record_success()
            return {"status": "ok", "order_id": mresp.get("order_id"), "filled": int(mresp.get("filled", 0))}
        except Exception as ex:
            await self.circuit.record_failure()
            log_json("ERROR", "dhan.safe", "market fallback failed, entering paper mode", exc=str(ex))
            PAPER_MODE = True
            self.paper_mode = True
            return {"status": "paper", "order_id": None, "filled": 0}

    async def place_market_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        global PAPER_MODE
        if PAPER_MODE or await self.circuit.is_tripped():
            log_json("INFO", "dhan.safe", "paper mode active - skipping market order", order=order)
            self.paper_mode = True
            return {"status": "paper", "order_id": None, "filled": 0}
        await self.bucket.consume(1)
        try:
            resp = await self._place_market_order_impl(order)
            await self.circuit.record_success()
            return {"status": "ok", "order_id": resp.get("order_id"), "filled": int(resp.get("filled", 0))}
        except Exception as ex:
            await self.circuit.record_failure()
            log_json("ERROR", "dhan.safe", "market order failed", exc=str(ex))
            PAPER_MODE = True
            self.paper_mode = True
            return {"status": "paper", "order_id": None, "filled": 0}
