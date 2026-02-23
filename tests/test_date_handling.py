# tests/test_date_handling.py
import pandas as pd
from analytics.train_meta_model import _ensure_trade_date_col

def _make_df_with_col(colname, values):
    return pd.DataFrame({colname: values, "label": [0,1,0]})

def test_ensure_trade_date_from_trade_date():
    df = _make_df_with_col("trade_date", ["2020-01-01","2020-01-02","2020-01-03"])
    out = _ensure_trade_date_col(df)
    assert "trade_date" in out.columns
    assert out["trade_date"].dtype == "datetime64[ns]"

def test_ensure_trade_date_from_date():
    df = _make_df_with_col("date", ["2020-01-01","2020-01-02","2020-01-03"])
    out = _ensure_trade_date_col(df)
    assert "trade_date" in out.columns

def test_ensure_trade_date_from_index():
    df = pd.DataFrame({"label":[0,1,0]}, index=pd.to_datetime(["2020-01-01","2020-01-02","2020-01-03"]))
    out = _ensure_trade_date_col(df)
    assert "trade_date" in out.columns
