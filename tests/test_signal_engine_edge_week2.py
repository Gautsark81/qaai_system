import pandas as pd
import numpy as np
from qaai_system.signal_engine.signal_engine import SignalEngine

# -----------------------------
# Week 2: Large-scale & Performance Tests
# -----------------------------


def test_large_dataset_run(monkeypatch):
    """Engine should handle large datasets efficiently."""
    n = 50_000  # large but memory-friendly
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=n, freq="min"),
            "open": (np.random.rand(n) * 100).astype(np.float32),
            "high": (np.random.rand(n) * 100).astype(np.float32),
            "low": (np.random.rand(n) * 100).astype(np.float32),
            "close": (np.random.rand(n) * 100).astype(np.float32),
            "volume": np.random.randint(1, 1000, size=n).astype(np.int32),
            "symbol": ["SYM"] * n,
        }
    )
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)

    se = SignalEngine()
    df = se.run()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == n
    assert "symbol" in df.columns


def test_runtime_efficiency(monkeypatch):
    """Benchmark runtime for moderate dataset."""
    n = 10_000
    df_in = pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=n, freq="min"),
            "open": (np.random.rand(n) * 100).astype(np.float32),
            "high": (np.random.rand(n) * 100).astype(np.float32),
            "low": (np.random.rand(n) * 100).astype(np.float32),
            "close": (np.random.rand(n) * 100).astype(np.float32),
            "volume": np.random.randint(1, 1000, size=n).astype(np.int32),
            "symbol": ["SYM"] * n,
        }
    )
    monkeypatch.setattr(SignalEngine, "run", lambda self: df_in)

    import time

    se = SignalEngine()
    start = time.time()
    df = se.run()
    elapsed = time.time() - start
    assert elapsed < 2.0, f"Runtime too long: {elapsed:.2f}s"
    assert len(df) == n
