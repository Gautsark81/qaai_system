"""
Simple job runner examples for export tasks.
"""

import argparse
from ml.export_preds_to_parquet import export_predictions_to_parquet
from ml.overlay_exporter import export_overlay
import sqlite3
import pandas as pd


def run_export_predictions(db: str, out: str, archive: bool):
    return export_predictions_to_parquet(db, out, archive=archive)


def run_overlay_from_db(db: str, overlay_out: str, raw_signals_parquet: str = None):
    # read preds from sqlite
    conn = sqlite3.connect(db)
    try:
        df = pd.read_sql_query(
            "SELECT symbol, timestamp, timeframe, prediction, probability, model_version, created_at FROM predictions",
            conn,
        )
    finally:
        conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return export_overlay(df, overlay_out, raw_signals_path=raw_signals_parquet)


def cli_main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("export_preds")
    p1.add_argument("--db", required=True)
    p1.add_argument("--out", required=True)
    p1.add_argument("--archive", action="store_true")

    p2 = sub.add_parser("overlay")
    p2.add_argument("--db", required=True)
    p2.add_argument("--out", required=True)
    p2.add_argument("--raw", required=False)

    args = parser.parse_args()
    if args.cmd == "export_preds":
        res = run_export_predictions(args.db, args.out, args.archive)
        print(res)
    elif args.cmd == "overlay":
        res = run_overlay_from_db(args.db, args.out, args.raw)
        print(res)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli_main()
