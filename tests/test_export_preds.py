# tests/test_export_preds.py
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

from ml.export_preds_to_parquet import do_export, read_last_export_ts, init_sample_db


def create_temp_db(path: Path, rows=3):
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    try:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS predictions")
        cur.execute(
            """
            CREATE TABLE predictions (
                ts TEXT,
                order_id TEXT,
                symbol TEXT,
                side TEXT,
                qty REAL,
                price REAL,
                nav REAL,
                last_price REAL,
                p_fill REAL,
                model_version TEXT,
                outcome_status TEXT
            )
            """
        )
        now = datetime.utcnow()
        sample = []
        for i in range(rows):
            ts = (now - timedelta(minutes=i)).isoformat()
            sample.append(
                (
                    ts,
                    f"ord_{i:03d}",
                    "SYM",
                    "buy",
                    1.0 + i,
                    100.0 + i,
                    1000.0,
                    100.0 + i,
                    0.5,
                    "v1",
                    "open",
                )
            )
        cur.executemany(
            "INSERT INTO predictions (ts,order_id,symbol,side,qty,price,nav,last_price,p_fill,model_version,outcome_status) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            sample,
        )
        conn.commit()
    finally:
        conn.close()


def test_export_writes_parquet_and_updates_marker(tmp_path):
    db_file = tmp_path / "test_ml_predictions.db"
    out_dir = tmp_path / "parquet_out"
    create_temp_db(db_file, rows=4)

    # ensure no marker initially
    assert read_last_export_ts(db_file) is None

    # run export with update_marker
    written_files, rows_exported = do_export(
        db_path=db_file,
        out_dir=out_dir,
        since=None,
        archive=False,
        delete=False,
        update_marker=True,
        force=False,
        compression=None,
        verbose=False,
    )

    # assert rows exported > 0 and we wrote at least one parquet
    assert rows_exported == 4
    assert len(written_files) >= 1
    # check a parquet exists and is readable
    pf = written_files[0]
    assert pf.exists()
    df = pd.read_parquet(pf)
    assert not df.empty
    assert "order_id" in df.columns

    # marker updated
    marker = read_last_export_ts(db_file)
    assert marker is not None
    # marker must be an ISO timestamp string parseable by pandas
    parsed = pd.to_datetime(marker)
    assert pd.notna(parsed)


def test_init_sample_db_creates_table(tmp_path):
    db_file = tmp_path / "sample.db"
    # call init_sample_db and check predictions table exists and has rows
    init_sample_db(db_file)
    conn = sqlite3.connect(str(db_file))
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(1) FROM predictions")
        count = cur.fetchone()[0]
        assert count == 2
    finally:
        conn.close()
