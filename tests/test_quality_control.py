import pandas as pd
import numpy as np

from qaai_system.signal_engine.quality_control import (
    evaluate_signal_quality,
    auto_tune_thresholds,
)


def mock_trade_log():
    np.random.seed(42)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=100),
            "symbol": [f"SYM{i % 10}" for i in range(100)],
            "pnl": np.random.normal(loc=20, scale=50, size=100),
        }
    )


def test_evaluate_signal_quality_structure():
    trade_log = mock_trade_log()
    result = evaluate_signal_quality(trade_log)

    assert "symbol" in result.columns
    assert "quality_score" in result.columns
    assert result.shape[0] <= 10


def test_evaluate_signal_quality_score_range():
    trade_log = mock_trade_log()
    result = evaluate_signal_quality(trade_log)

    assert result["quality_score"].between(0, 1).all()


def test_auto_tune_thresholds_output():
    trade_log = mock_trade_log()
    result = auto_tune_thresholds(trade_log)

    assert set(result.keys()) == {
        "confidence_threshold",
        "sl_multiplier",
        "tp_multiplier",
    }
    assert 0.3 <= result["confidence_threshold"] <= 0.7
    assert result["sl_multiplier"] > 0
    assert result["tp_multiplier"] > 0


def test_auto_tune_thresholds_minimal_inputs():
    thresholds = auto_tune_thresholds(
        mock_trade_log(), current_buy=0.5, current_sell=0.5
    )

    assert thresholds is not None
    assert "confidence_threshold" in thresholds
    assert "sl_multiplier" in thresholds
    assert "tp_multiplier" in thresholds
