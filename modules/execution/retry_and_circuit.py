# modules/execution/retry_and_circuit.py
import time
from typing import Callable

class CircuitBreaker:
    def __init__(self, fail_max: int = 5, reset_timeout: float = 30.0):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self._fail_count = 0
        self._last_failure = 0.0
        self._open = False

    def allow_request(self) -> bool:
        if not self._open:
            return True
        if time.time() - self._last_failure > self.reset_timeout:
            # half-open
            self._open = False
            self._fail_count = 0
            return True
        return False

    def success(self):
        self._fail_count = 0
        self._open = False

    def failure(self):
        self._fail_count += 1
        self._last_failure = time.time()
        if self._fail_count >= self.fail_max:
            self._open = True

def retry_with_backoff(fn: Callable, retries: int = 3, base_delay: float = 0.2):
    last_exc = None
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            time.sleep(base_delay * (2 ** i))
    # final attempt (let exception propagate)
    return fn()
