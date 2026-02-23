#!/usr/bin/env python3
from infra.sqlite_client import SQLiteClient


def check(db_path):
    db = SQLiteClient(db_path)
    tables = ["ohlcv", "ticks", "features", "ml_predictions"]
    for t in tables:
        try:
            rows = db.fetchall(f"SELECT count(1) as cnt FROM {t}")
            cnt = rows[0]["cnt"] if rows else 0
            print(f"{db_path} {t}: {cnt} rows")
        except Exception as e:
            print(f"{db_path} {t}: ERROR ({e})")


if __name__ == "__main__":
    check("db/ohlcv.db")
    check("db/ticks.db")
    check("db/features.db")
    check("data/ml_predictions.db")
