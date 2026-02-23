# qaai_system/market/ticks.py
from __future__ import annotations

import datetime as dt
import threading
import queue
from dataclasses import dataclass
from typing import Callable, Optional, Protocol, List


@dataclass
class Tick:
    """
    Minimal tick representation used by the intraday pipeline.

    Attributes
    ----------
    symbol : str
        Instrument name, e.g. 'NIFTY', 'BANKNIFTY'.
    ts : datetime
        Exchange timestamp (timezone-aware preferred).
    price : float
        Last traded price (LTP).
    qty : float
        Traded quantity for this tick.
    bid : Optional[float]
        Best bid (optional).
    ask : Optional[float]
        Best ask (optional).
    """
    symbol: str
    ts: dt.datetime
    price: float
    qty: float
    bid: Optional[float] = None
    ask: Optional[float] = None


class TickHandler(Protocol):
    def __call__(self, tick: Tick) -> None:
        ...


class TickSource(Protocol):
    """
    Protocol for any live tick source (e.g., Dhan, websocket, replay).

    Implementations should call all registered handlers for each incoming tick.
    """

    def subscribe(self, handler: TickHandler) -> None:
        ...

    def close(self) -> None:
        ...


class InMemoryTickBus(TickSource):
    """
    Simple in-process tick bus.

    Use this for:
      - unit/integration tests of live pipeline pieces
      - playing back historical ticks into the live feature/ohlcv pipeline
      - feeding strategies in paper mode

    Example
    -------
        bus = InMemoryTickBus()
        bus.subscribe(my_handler)

        bus.publish(Tick(symbol="NIFTY", ts=dt.datetime.utcnow(), price=24000, qty=50))
    """

    def __init__(self, max_queue: int = 10_000) -> None:
        self._handlers: List[TickHandler] = []
        self._q: "queue.Queue[Tick]" = queue.Queue(maxsize=max_queue)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def subscribe(self, handler: TickHandler) -> None:
        """Register a handler that will receive all ticks."""
        self._handlers.append(handler)

    def publish(self, tick: Tick) -> None:
        """Push a tick into the bus (non-blocking where possible)."""
        try:
            self._q.put_nowait(tick)
        except queue.Full:
            # safest behaviour: drop the tick but do not crash
            # you can log here if you pass a logger
            pass

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                tick = self._q.get(timeout=0.5)
            except queue.Empty:
                continue

            for h in list(self._handlers):
                try:
                    h(tick)
                except Exception:
                    # handler failures must not kill the bus
                    # hook your logger here if needed
                    continue

    def close(self) -> None:
        self._stop.set()
        try:
            self._thread.join(timeout=1.0)
        except Exception:
            pass
