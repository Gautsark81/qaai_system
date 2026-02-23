"""
modules/performance/timers.py

High-resolution timing utilities.
"""

import time
from contextlib import contextmanager


@contextmanager
def timed():
    start = time.perf_counter()
    yield lambda: (time.perf_counter() - start) * 1000.0
