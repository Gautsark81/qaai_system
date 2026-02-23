### 📁 FILE: tests/test_audit_loader.py

import tempfile
import pandas as pd
from streamlit_app.utils.audit_loader import load_trade_data


def test_load_trade_data_csv(monkeypatch):
    sample_data = pd.DataFrame(
        {
            "timestamp": ["2023-01-01 10:00:00", "2023-01-01 11:00:00"],
            "symbol": ["AAPL", "GOOG"],
            "strategy_id": ["S1", "S1"],
            "status": ["FILLED", "REJECTED"],
            "pnl": [100, -50],
            "stop_loss": [90, 85],
            "take_profit": [110, 95],
        }
    )
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
        sample_data.to_csv(tmp.name, index=False)
        monkeypatch.setattr("streamlit_app.utils.audit_loader.CSV_LOG_PATH", tmp.name)
        df = load_trade_data(source="csv")

    assert not df.empty
    assert set(df.columns) >= {"timestamp", "symbol", "strategy_id", "status", "pnl"}
    assert df["status"].isin(["FILLED"]).all()  # Only valid statuses remain


def test_missing_file(monkeypatch):
    monkeypatch.setattr(
        "streamlit_app.utils.audit_loader.CSV_LOG_PATH", "nonexistent.csv"
    )
    try:
        load_trade_data(source="csv")
    except FileNotFoundError:
        assert True
    else:
        assert False


def test_invalid_source():
    try:
        load_trade_data(source="xml")
    except ValueError:
        assert True
    else:
        assert False
