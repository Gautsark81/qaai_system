# tests/test_drift_detector.py
from ml.drift_detector import DriftWatcher
import random

def test_drift_watcher_detects_change():
    dw = DriftWatcher()
    # feed stable values first
    detected = False
    for _ in range(200):
        if dw.update(0.1):
            detected = True
            break
    # unlikely to detect drift on stable data
    assert detected is False
    # feed a significant change -> ADWIN should detect at some point
    drift_found = False
    for v in [0.1] * 50 + [1.0] * 200:
        if dw.update(v):
            drift_found = True
            break
    assert drift_found is True
