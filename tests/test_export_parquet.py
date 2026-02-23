import sqlite3
import json
import pandas as pd

# import the exporter module
import ml.export_preds_to_parquet as exporter


def test_normalize_predictions_df_timestamp_and_sym():
    # dataframe with 'timestamp' and 'sym' fields should normalize to ts & symbol & date
    df_raw = pd.DataFrame(
        {
            "timestamp": ["2025-01-01T09:15:00", "2025-01-01T09:20:00"],
            "sym": ["TEST", "TEST"],
            "pred": [1, 0],
            "prob": [0.9, 0.2],
        }
    )
    norm = exporter._normalize_predictions_df(df_raw)
    assert "ts" in norm.columns
    assert "symbol" in norm.columns
    assert "date" in norm.columns
    assert "prediction" in norm.columns  # pred -> prediction mapping
    assert norm["symbol"].iloc[0] == "TEST"
    # dates derived correctly
    assert norm["date"].iloc[0] == "2025-01-01"


def test_do_export_writes_parquet_and_meta(tmp_path):
    # Create a sample DB with the module helper
    db_path = tmp_path / "test_preds.db"
    out_dir = tmp_path / "parquet_out"

    # init sample DB (module helper)
    exporter.init_sample_db(db_path)

    # run export (no compression to avoid engine issues in constrained environments)
    written_files, rows = exporter.do_export(
        db_path=db_path,
        out_dir=out_dir,
        since=None,
        archive=False,
        delete=False,
        update_marker=False,
        force=True,
        compression=None,
        verbose=True,
    )

    # Check rows/counts
    assert rows > 0
    # At least one parquet file written
    files = list(out_dir.rglob("*.parquet"))
    assert len(files) > 0

    # Check that _meta.json exists under one of partition folders
    metas = list(out_dir.rglob("_meta.json"))
    assert len(metas) > 0
    meta = json.loads(metas[0].read_text(encoding="utf-8"))
    assert "rows" in meta and meta["rows"] >= 0
    assert "schema_version" in meta


def test_do_export_respects_since_filter(tmp_path):
    # Create DB and insert two rows with different ts, then export with since filter
    db_path = tmp_path / "since_test.db"
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE predictions (ts TEXT, order_id TEXT, symbol TEXT, created_at TEXT)"
        )
        # older row
        cur.execute(
            "INSERT INTO predictions (ts, order_id, symbol, created_at) VALUES (?, ?, ?, ?)",
            ("2024-12-01T00:00:00", "o1", "X", "2024-12-01T00:00:00"),
        )
        # newer row
        cur.execute(
            "INSERT INTO predictions (ts, order_id, symbol, created_at) VALUES (?, ?, ?, ?)",
            ("2025-01-10T00:00:00", "o2", "Y", "2025-01-10T00:00:00"),
        )
        conn.commit()
    finally:
        conn.close()

    out_dir = tmp_path / "parquet_since"
    # export since 2025-01-01 should include only the newer row
    written_files, rows = exporter.do_export(
        db_path=db_path,
        out_dir=out_dir,
        since="2025-01-01",
        archive=False,
        delete=False,
        update_marker=False,
        force=True,
        compression=None,
        verbose=False,
    )

    # Expect 1 row exported (the 2025-01-10 row)
    assert rows == 1
    # Parquet content matches
    files = list(out_dir.rglob("*.parquet"))
    assert len(files) > 0
    df = pd.read_parquet(files[0])
    # there should be at least one row with symbol 'Y'
    assert "Y" in df["symbol"].values or (df["symbol"].astype(str) == "Y").any()
