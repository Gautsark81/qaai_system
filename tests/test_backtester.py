import pytest
import pandas as pd
from backtest.backtester import Backtester


@pytest.fixture
def mock_ohlcv():
    date_range = pd.date_range("2023-01-01", periods=100, freq="5min")
    data = {
        "open": [100 + i for i in range(100)],
        "high": [101 + i for i in range(100)],
        "low": [99 + i for i in range(100)],
        "close": [100 + (i % 5 - 2) for i in range(100)],
        "volume": [1000 + i for i in range(100)],
    }
    return pd.DataFrame(data, index=date_range)


@pytest.fixture
def mock_signals():
    timestamps = pd.date_range("2023-01-01", periods=90, freq="5min")[10:]
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "symbol": "RELIANCE",
            "signal": ["BUY" if i % 2 == 0 else "SELL" for i in range(len(timestamps))],
            "confidence": [0.9 for _ in range(len(timestamps))],
        }
    )


def test_backtest_strategy_metrics(mock_ohlcv, mock_signals):
    backtester = Backtester()
    trades, stats = backtester.run(
        symbol="RELIANCE", ohlcv=mock_ohlcv, signals=mock_signals
    )

    # Ensure trade records exist
    assert isinstance(trades, list)
    assert all("pnl" in trade for trade in trades)

    # Validate metrics
    assert isinstance(stats, dict)
    assert "total_return" in stats
    assert "win_rate" in stats
    assert "sharpe_ratio" in stats
    assert "max_drawdown" in stats

    # Basic bounds
    assert -100 <= stats["total_return"] <= 100
    assert 0 <= stats["win_rate"] <= 1
    assert isinstance(stats["sharpe_ratio"], (int, float))
    assert stats["max_drawdown"] >= 0  # drawdown is a positive number
    print(f"✅ Metrics OK: {stats}")
