import time
import threading

class TokenBucket:
    """
    Simple thread-safe token bucket.
    capacity: max tokens
    refill_rate_per_sec: tokens added per second (float)
    """
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.rate = float(refill_rate_per_sec)
        self.lock = threading.Lock()
        self.last = time.time()

    def consume(self, tokens: int = 1) -> bool:
        with self.lock:
            now = time.time()
            delta = now - self.last
            if delta > 0:
                refill = delta * self.rate
                self.tokens = min(self.capacity, self.tokens + refill)
                self.last = now
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_tokens(self) -> float:
        with self.lock:
            # refresh tokens
            now = time.time()
            delta = now - self.last
            refill = delta * self.rate
            self.tokens = min(self.capacity, self.tokens + refill)
            self.last = now
            return self.tokens
