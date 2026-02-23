import os
import tempfile
import sqlite3
from ml.predict import make_predictions_for_symbol
from ml.save_predictions import save_predictions_df, read_predictions_count
from ml.helpers.validation import validate_predictions_df


def test_make_predictions_basic():
    df = make_predictions_for_symbol(
        "TESTSYM", "2025-01-01", "2025-01-01T00:20:00", timeframe="5m", seed=123
    )
    # expected 5-minute buckets: 00:00,00:05,00:10,00:15,00:20 -> 5 rows
    assert len(df) == 5
    # columns
    for c in [
        "symbol",
        "timestamp",
        "timeframe",
        "prediction",
        "probability",
        "model_version",
    ]:
        assert c in df.columns
    # probabilities between 0 and 1
    assert df["probability"].min() >= 0.0 and df["probability"].max() <= 1.0
    validate_predictions_df(df)


def test_save_and_read_sqlite_roundtrip():
    df = make_predictions_for_symbol(
        "TSYM", "2025-02-02", "2025-02-02T00:10:00", timeframe="5m", seed=7
    )
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, "preds.db")
        # save
        save_predictions_df(df, db_path, meta_out=os.path.join(td, "meta.json"))
        # ensure DB has rows
        cnt = read_predictions_count(db_path)
        assert cnt == len(df)
        # query and assert schema/values
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT symbol, timestamp, timeframe, prediction, probability, model_version, created_at FROM predictions"
        )
        rows = cur.fetchall()
        assert len(rows) == len(df)
        # basic check first row symbol
        assert rows[0][0] == "TSYM"
        conn.close()
