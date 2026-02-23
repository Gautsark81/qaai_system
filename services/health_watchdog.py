from __future__ import annotations
import time
import logging
import threading

logger = logging.getLogger("health_watchdog")


class Heartbeat:
    def __init__(self, timeout_sec: int = 60):
        self.timeout = timeout_sec
        self._last = time.time()
        self._lock = threading.Lock()

    def beat(self):
        with self._lock:
            self._last = time.time()

    def stale(self) -> bool:
        with self._lock:
            return (time.time() - self._last) > self.timeout


def run_watchdog(on_stale_callback, interval=15, timeout=60):
    hb = Heartbeat(timeout_sec=timeout)

    def loop():
        while True:
            time.sleep(interval)
            if hb.stale():
                try:
                    on_stale_callback()
                except Exception:
                    logger.exception("watchdog recovery failed")

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    return hb
