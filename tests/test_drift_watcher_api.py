# tests/test_drift_watcher_api.py
from ml.drift_detector import DriftWatcher
class DummyAdwin:
    def update(self, x): return False
def test_drift_update_with_update_api():
    dw = DriftWatcher(adwin=DummyAdwin())
    assert dw.update(1.0) is False

def test_drift_update_with_missing_api_returns_false():
    class Bad:
        pass
    dw = DriftWatcher(adwin=Bad())
    assert dw.update(1.0) is False
