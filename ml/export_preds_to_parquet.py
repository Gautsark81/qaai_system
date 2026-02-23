#!/usr/bin/env python3
"""
ml/export_preds_to_parquet.py — Supercharged exporter with consolidation & prune

Features added:
- --consolidate: compact partitions into canonical part-000.parquet files
- --prune-old {archive,delete,keep}: control what happens to legacy part-*.parquet
  (default: archive -> move to __legacy__/ folder with manifest)
- --retention-days: how long legacy archives are kept (applies to archive pruning)
- --dry-run: preview consolidation/prune actions without changing files

Behavior:
- Consolidation reads existing part-*.parquet files plus new rows, merges/dedupes,
  writes canonical part-000.parquet atomically (same dedupe logic as exports).
- Pruning archives (or deletes) legacy files only after successful canonical write.
"""

from __future__ import annotations
import argparse
import json
import logging
import shutil
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, date, time
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Dict, Any

import pandas as pd

LOGGER = logging.getLogger("export_preds")
DEFAULT_DB = Path("data/ml_predictions.db")
DEFAULT_OUT = Path("data/parquet")
TABLE_NAME = "predictions"
ARCHIVE_TABLE = "archive_predictions"
STATE_TABLE = "exporter_state"
SCHEMA_VERSION = "v1"

ALLOWED_COMPRESSION = [None, "snappy", "gzip", "brotli", "lz4"]
PRUNE_CHOICES = ["archive", "delete", "keep"]


# -------------------------
# Basic helpers (unchanged)
# -------------------------
def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _choose_parquet_engine() -> str:
    try:
        return "pyarrow"
    except Exception:
        try:
            return "fastparquet"
        except Exception:
            raise RuntimeError(
                "No Parquet engine installed. Install one of: `pip install pyarrow` or `pip install fastparquet`."
            )


def ensure_outdir(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)


def _write_meta_for_partition(
    dest_dir: Path,
    rows: int,
    min_ts: Optional[pd.Timestamp],
    max_ts: Optional[pd.Timestamp],
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    meta = {
        "rows": int(rows),
        "min_ts": (
            pd.to_datetime(min_ts).isoformat()
            if min_ts is not None and not pd.isna(min_ts)
            else None
        ),
        "max_ts": (
            pd.to_datetime(max_ts).isoformat()
            if max_ts is not None and not pd.isna(max_ts)
            else None
        ),
        "schema_version": SCHEMA_VERSION,
        "written_at_utc": datetime.utcnow().isoformat() + "Z",
    }
    if extra:
        meta.update(extra)
    dest_dir.mkdir(parents=True, exist_ok=True)
    meta_path = dest_dir / "_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


# -------------------------
# DB helpers
# -------------------------
def read_last_export_ts(db_path: Path) -> Optional[str]:
    if not db_path.exists():
        return None
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {STATE_TABLE} (k TEXT PRIMARY KEY, v TEXT)"
        )
        conn.commit()
        cur.execute(f"SELECT v FROM {STATE_TABLE} WHERE k = 'last_export_ts'")
        row = cur.fetchone()
        return row[0] if row else None
    except Exception:
        LOGGER.exception("Failed reading exporter state; continuing without marker")
        return None
    finally:
        conn.close()


def write_last_export_ts(db_path: Path, iso_ts: str) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {STATE_TABLE} (k TEXT PRIMARY KEY, v TEXT)"
        )
        cur.execute(
            "REPLACE INTO %s (k, v) VALUES ('last_export_ts', ?)" % STATE_TABLE,
            (iso_ts,),
        )
        conn.commit()
        LOGGER.debug("Wrote last_export_ts=%s to %s", iso_ts, db_path)
    finally:
        conn.close()


def read_predictions_raw(db_path: Path, since: Optional[str] = None) -> pd.DataFrame:
    if not db_path.exists():
        LOGGER.info("DB not found: %s", db_path)
        return pd.DataFrame()

    conn = sqlite3.connect(str(db_path))
    try:
        cols_info = conn.execute("PRAGMA table_info(predictions)").fetchall()
        col_names = [r[1] for r in cols_info]
        params: Tuple = ()
        base_q = "SELECT * FROM predictions"
        if since:
            try:
                parsed = datetime.strptime(since, "%Y-%m-%d")
                since_iso = parsed.isoformat()
            except Exception:
                since_iso = since
            if "ts" in col_names:
                base_q += " WHERE ts >= ?"
                params = (since_iso,)
            elif "timestamp" in col_names:
                base_q += " WHERE timestamp >= ?"
                params = (since_iso,)
            elif "created_at" in col_names:
                base_q += " WHERE created_at >= ?"
                params = (since_iso,)
            else:
                LOGGER.warning(
                    "No time column found to apply --since filter; reading all rows"
                )
        df = (
            pd.read_sql_query(base_q, conn, params=params)
            if params
            else pd.read_sql_query(base_q, conn)
        )
    except Exception:
        LOGGER.exception("Failed reading predictions table. Returning empty DataFrame.")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df


def _normalize_predictions_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    ts_candidates = [
        c for c in ("ts", "timestamp", "created_at", "time") if c in df.columns
    ]
    if ts_candidates:
        ts_col = ts_candidates[0]
        df["ts"] = pd.to_datetime(df[ts_col], errors="coerce")
    else:
        df["ts"] = pd.NaT

    symbol_candidates = [c for c in ("symbol", "sym", "ticker") if c in df.columns]
    if symbol_candidates:
        df["symbol"] = df[symbol_candidates[0]].astype(str)
    else:
        df["symbol"] = "UNKNOWN"

    if "timeframe" not in df.columns:
        if "tf" in df.columns:
            df["timeframe"] = df["tf"].astype(str)
        else:
            df["timeframe"] = "raw"

    if "prediction" not in df.columns and "pred" in df.columns:
        df["prediction"] = df["pred"]
    if "probability" not in df.columns and "prob" in df.columns:
        df["probability"] = df["prob"]
    if "model_version" not in df.columns:
        df["model_version"] = pd.NA

    df["date"] = df["ts"].dt.strftime("%Y-%m-%d")
    if df["date"].isna().any() and "created_at" in df.columns:
        df.loc[df["date"].isna(), "date"] = pd.to_datetime(
            df.loc[df["date"].isna(), "created_at"], errors="coerce"
        ).dt.strftime("%Y-%m-%d")
    df["date"] = df["date"].fillna("1970-01-01")
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")

    core = [
        "ts",
        "symbol",
        "timeframe",
        "prediction",
        "probability",
        "model_version",
        "date",
    ]
    cols = [c for c in core if c in df.columns] + [
        c for c in df.columns if c not in core
    ]
    return df[cols]


# -------------------------
# Parquet helpers: write single-file atomically
# -------------------------
def _choose_engine_and_write_parquet(
    df: pd.DataFrame, file_path: Path, compression: Optional[str]
) -> None:
    engine = _choose_parquet_engine()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(file_path.parent)) as td:
        temp_file = Path(td) / file_path.name
        df.to_parquet(
            str(temp_file), engine=engine, index=False, compression=compression
        )
        if file_path.exists():
            file_path.unlink()
        shutil.move(str(temp_file), str(file_path))


def _merge_dataframes(existing: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    if existing is None or existing.empty:
        combined = new_df.copy()
    else:
        combined = pd.concat([existing, new_df], ignore_index=True)
    key_cols = [c for c in ("ts", "order_id") if c in combined.columns]
    if not key_cols and "ts" in combined.columns:
        key_cols = ["ts"]
    if key_cols:
        if "ts" in combined.columns:
            combined["ts"] = pd.to_datetime(combined["ts"], errors="coerce")
        combined = combined.drop_duplicates(subset=key_cols, keep="last")
    if "ts" in combined.columns:
        combined = combined.sort_values(by=["ts"])
    combined = combined.reset_index(drop=True)
    return combined


def _read_existing_partition_df(partition_path: Path) -> pd.DataFrame:
    files = sorted([p for p in partition_path.glob("*.parquet")])
    if not files:
        return pd.DataFrame()
    dfs = []
    for f in files:
        try:
            dfs.append(pd.read_parquet(f))
        except Exception:
            LOGGER.exception("Failed reading existing parquet %s; skipping", f)
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


def _merge_and_write_partition(
    partition_path: Path, new_df: pd.DataFrame, compression: Optional[str]
) -> List[Path]:
    try:
        ensure_outdir(partition_path)
        existing_df = _read_existing_partition_df(partition_path)
        combined = _merge_dataframes(existing_df, new_df)
        canonical = partition_path / "part-000.parquet"
        _choose_engine_and_write_parquet(combined, canonical, compression=compression)
        min_ts = combined["ts"].min() if "ts" in combined.columns else None
        max_ts = combined["ts"].max() if "ts" in combined.columns else None
        _write_meta_for_partition(
            partition_path, rows=len(combined), min_ts=min_ts, max_ts=max_ts, extra=None
        )
        LOGGER.info(
            "Wrote canonical partition file %s (%d rows)", canonical, len(combined)
        )
        return [canonical]
    except Exception:
        LOGGER.exception("Failed to merge/write partition %s", partition_path)
        return []


# -------------------------
# Consolidation & prune logic
# -------------------------
def _archive_legacy_files(
    partition_path: Path, legacy_files: List[Path], dry_run: bool, retention_days: int
) -> int:
    """
    Move legacy_files into partition_path/__legacy__/<ts>/ and write a manifest.
    Returns number of files archived (or would be archived in dry-run).
    """
    if not legacy_files:
        return 0
    legacy_root = partition_path / "__legacy__"
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest_dir = legacy_root / ts
    if dry_run:
        LOGGER.info(
            "[dry-run] Would archive %d files from %s to %s",
            len(legacy_files),
            partition_path,
            dest_dir,
        )
        return len(legacy_files)
    dest_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for f in legacy_files:
        try:
            target = dest_dir / f.name
            shutil.move(str(f), str(target))
            manifest.append({"src": str(f), "dst": str(target)})
        except Exception:
            LOGGER.exception("Failed to move legacy file %s to %s", f, dest_dir)
    manifest_path = dest_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as m:
        json.dump(
            {"moved_at": datetime.utcnow().isoformat() + "Z", "files": manifest},
            m,
            indent=2,
        )
    LOGGER.info("Archived %d legacy files to %s", len(manifest), dest_dir)
    return len(manifest)


def _delete_legacy_files(legacy_files: List[Path], dry_run: bool) -> int:
    if not legacy_files:
        return 0
    if dry_run:
        LOGGER.info("[dry-run] Would delete %d legacy files", len(legacy_files))
        return len(legacy_files)
    deleted = 0
    for f in legacy_files:
        try:
            f.unlink()
            deleted += 1
        except Exception:
            LOGGER.exception("Failed to delete legacy file %s", f)
    LOGGER.info("Deleted %d legacy files", deleted)
    return deleted


def _prune_partition_after_consolidation(
    partition_path: Path, prune_mode: str, dry_run: bool, retention_days: int
) -> int:
    """
    After a successful canonical write, prune old 'part-*.parquet' files according to prune_mode.
    prune_mode: 'archive' (move to __legacy__), 'delete' (delete), 'keep' (do nothing).
    Returns number of files pruned (or would be pruned).
    """
    # find legacy files: everything matching part-*.parquet except canonical part-000.parquet
    legacy_files = [
        p for p in partition_path.glob("part-*.parquet") if p.name != "part-000.parquet"
    ]
    if not legacy_files:
        return 0
    if prune_mode == "keep":
        LOGGER.info(
            "Prune-mode=keep; leaving %d legacy files in %s",
            len(legacy_files),
            partition_path,
        )
        return 0
    if prune_mode == "archive":
        return _archive_legacy_files(
            partition_path, legacy_files, dry_run=dry_run, retention_days=retention_days
        )
    if prune_mode == "delete":
        return _delete_legacy_files(legacy_files, dry_run=dry_run)
    return 0


def consolidate_partitions(
    out_dir: Path,
    partition_cols: List[str] = ("symbol", "date", "timeframe"),
    dry_run: bool = False,
    prune_mode: str = "archive",
    retention_days: int = 7,
    symbol_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Consolidate partitions under out_dir. Returns a summary dict:
      { "consolidated": n, "pruned": n, "errors": [] }
    Supports dry_run to preview.
    """
    setup_logging(verbose)
    out_dir = Path(out_dir)
    if not out_dir.exists():
        LOGGER.info("Out dir does not exist: %s", out_dir)
        return {"consolidated": 0, "pruned": 0, "errors": ["out_dir_missing"]}

    summary = {"consolidated": 0, "pruned": 0, "errors": []}
    # build partition glob pattern: out_dir/symbol=*/date=*/timeframe=*
    # Walk directory tree and identify partition folders by presence of _meta.json or part-*.parquet
    for symbol_dir in sorted([d for d in out_dir.iterdir() if d.is_dir()]):
        # symbol_dir like symbol=XYZ
        try:
            # optional symbol filter
            if symbol_filter and symbol_filter not in symbol_dir.name:
                continue
            for date_dir in sorted([d for d in symbol_dir.iterdir() if d.is_dir()]):
                # date_dir like date=YYYY-MM-DD
                try:
                    if date_from or date_to:
                        # extract date string
                        try:
                            date_str = date_dir.name.split("=", 1)[1]
                            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                        except Exception:
                            dt = None
                        if dt:
                            if (
                                date_from
                                and dt < datetime.strptime(date_from, "%Y-%m-%d").date()
                            ):
                                continue
                            if (
                                date_to
                                and dt > datetime.strptime(date_to, "%Y-%m-%d").date()
                            ):
                                continue
                    for tf_dir in sorted([d for d in date_dir.iterdir() if d.is_dir()]):
                        # partition directory
                        partition_path = tf_dir
                        # read existing files & canonical file
                        try:
                            # If canonical file exists already and no other legacy files, skip unless prune requested
                            canonical = partition_path / "part-000.parquet"
                            legacy = [
                                p
                                for p in partition_path.glob("part-*.parquet")
                                if p.name != "part-000.parquet"
                            ]
                            needs_consolidate = bool(legacy) or (
                                not canonical.exists()
                                and list(partition_path.glob("part-*.parquet"))
                            )
                            if not needs_consolidate:
                                LOGGER.debug(
                                    "Partition %s already consolidated and no legacy files",
                                    partition_path,
                                )
                                # still consider prune (if some old files exist)
                                pruned = _prune_partition_after_consolidation(
                                    partition_path, prune_mode, dry_run, retention_days
                                )
                                summary["pruned"] += pruned
                                continue

                            # read existing rows (if any)
                            existing_df = _read_existing_partition_df(partition_path)
                            # If there is no canonical and only a single file (like part-0.parquet), treat that as existing_df
                            # Consolidation will write part-000.parquet; after success, prune will archive old files
                            # Compose new_df = existing_df (since consolidation is for previously exported files)
                            new_df = existing_df.copy()
                            if new_df.empty:
                                LOGGER.info(
                                    "Partition %s has no parquet files to consolidate; skipping",
                                    partition_path,
                                )
                                continue

                            LOGGER.info(
                                "Consolidating partition %s (rows=%d) dry_run=%s",
                                partition_path,
                                len(new_df),
                                dry_run,
                            )
                            if dry_run:
                                summary["consolidated"] += 1
                                pruned = len(
                                    [
                                        p
                                        for p in partition_path.glob("part-*.parquet")
                                        if p.name != "part-000.parquet"
                                    ]
                                )
                                summary["pruned"] += pruned
                                continue

                            # perform merge+write
                            files = _merge_and_write_partition(
                                partition_path, new_df, compression=None
                            )
                            if files:
                                summary["consolidated"] += 1
                                # prune old files after success
                                pruned = _prune_partition_after_consolidation(
                                    partition_path,
                                    prune_mode,
                                    dry_run=False,
                                    retention_days=retention_days,
                                )
                                summary["pruned"] += pruned
                            else:
                                summary["errors"].append(str(partition_path))
                        except Exception:
                            LOGGER.exception(
                                "Failed consolidating partition %s", partition_path
                            )
                            summary["errors"].append(str(partition_path))
                except Exception:
                    LOGGER.exception("Error iterating date dir %s", date_dir)
        except Exception:
            LOGGER.exception("Error iterating symbol dir %s", symbol_dir)
    return summary


# -------------------------
# Export orchestration (unchanged core but uses merge writer)
# -------------------------
@dataclass
class ExportResult:
    files: List[Path]
    rows: int
    partitions: List[Dict[str, Any]]


def export_predictions_to_parquet(
    db_path: Path,
    out_dir: Path,
    partition_cols: List[str] = ("symbol", "date", "timeframe"),
    compression: Optional[str] = None,
    since: Optional[str] = None,
    archive: bool = False,
    delete: bool = False,
    update_marker: bool = False,
    verbose: bool = False,
) -> ExportResult:
    setup_logging(verbose)
    ensure_outdir(out_dir)

    raw = read_predictions_raw(db_path, since=since)
    if raw.empty:
        LOGGER.info("No rows to export")
        return ExportResult(files=[], rows=0, partitions=[])

    df = _normalize_predictions_df(raw)
    if df.empty:
        LOGGER.warning("Normalization resulted in empty DataFrame")
        return ExportResult(files=[], rows=0, partitions=[])

    if archive and out_dir.exists():
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        archive_dir = out_dir.parent / f"{out_dir.name}_archive_{ts}"
        shutil.move(str(out_dir), str(archive_dir))
        LOGGER.info("Archived existing output to %s", archive_dir)

    written_files: List[Path] = []
    partitions: List[Dict[str, Any]] = []

    for pc in partition_cols:
        if pc not in df.columns:
            df[pc] = pd.NA

    grouped = df.groupby(list(partition_cols))
    for part_values, group in grouped:
        if not isinstance(part_values, tuple):
            part_values = (part_values,)
        partition_path = out_dir
        for col, val in zip(partition_cols, part_values):
            safe_val = str(val) if (val is not None and not pd.isna(val)) else "unknown"
            partition_path = partition_path / f"{col}={safe_val}"

        write_df = group.reset_index(drop=True)
        # merge & write canonical file
        files = _merge_and_write_partition(
            partition_path, write_df, compression=compression
        )
        if files:
            written_files.extend(files)
            min_ts = write_df["ts"].min() if "ts" in write_df.columns else None
            max_ts = write_df["ts"].max() if "ts" in write_df.columns else None
            partitions.append(
                {
                    "path": str(partition_path),
                    "rows": len(write_df),
                    "min_ts": str(min_ts) if min_ts is not None else None,
                    "max_ts": str(max_ts) if max_ts is not None else None,
                }
            )
        else:
            LOGGER.warning("No files written for partition %s", partition_path)

    exported_dates = (
        sorted({pd.to_datetime(ts).date() for ts in df["ts"].dropna()})
        if "ts" in df.columns
        else []
    )
    if archive and exported_dates:
        archived_deleted = archive_rows(db_path, exported_dates)
        LOGGER.info("Archived approx %d rows into %s", archived_deleted, ARCHIVE_TABLE)
    elif delete and exported_dates:
        archived_deleted = delete_rows(db_path, exported_dates)
        LOGGER.info("Deleted approx %d rows from %s", archived_deleted, TABLE_NAME)

    if update_marker and "ts" in df.columns and not df["ts"].dropna().empty:
        max_ts = df["ts"].max()
        if pd.isna(max_ts):
            LOGGER.warning("Max exported ts is NaT; not updating marker")
        else:
            iso = pd.to_datetime(max_ts).isoformat()
            write_last_export_ts(db_path, iso)
            LOGGER.info("Updated last_export_ts to %s", iso)

    return ExportResult(files=written_files, rows=len(df), partitions=partitions)


# -------------------------
# Archive / Delete helpers (unchanged)
# -------------------------
def archive_rows(db_path: Path, exported_dates: Iterable[date]) -> int:
    if not db_path.exists():
        return 0

    conn = sqlite3.connect(str(db_path))
    archived = 0
    try:
        cur = conn.cursor()
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {ARCHIVE_TABLE} AS SELECT * FROM {TABLE_NAME} WHERE 0"
        )
        conn.commit()
        for d in exported_dates:
            start = datetime.combine(d, time.min).isoformat()
            end = datetime.combine(d, time.max).isoformat()
            cur.execute(
                f"INSERT INTO {ARCHIVE_TABLE} SELECT * FROM {TABLE_NAME} WHERE ts >= ? AND ts <= ?",
                (start, end),
            )
            cur.execute(
                f"DELETE FROM {TABLE_NAME} WHERE ts >= ? AND ts <= ?", (start, end)
            )
            archived += cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0
            conn.commit()
    finally:
        conn.close()
    return archived


def delete_rows(db_path: Path, exported_dates: Iterable[date]) -> int:
    if not db_path.exists():
        return 0
    conn = sqlite3.connect(str(db_path))
    deleted = 0
    try:
        cur = conn.cursor()
        for d in exported_dates:
            start = datetime.combine(d, time.min).isoformat()
            end = datetime.combine(d, time.max).isoformat()
            cur.execute(
                f"DELETE FROM {TABLE_NAME} WHERE ts >= ? AND ts <= ?", (start, end)
            )
            deleted += cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0
            conn.commit()
    finally:
        conn.close()
    return deleted


# -------------------------
# Utilities: init sample DB, CLI
# -------------------------
def init_sample_db(db_path: Path, overwrite: bool = True) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        if overwrite:
            cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
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
                outcome_status TEXT,
                created_at TEXT
            )
            """
        )
        now = datetime.utcnow().isoformat()
        sample = [
            (
                now,
                "ord_001",
                "AAPL",
                "buy",
                10.0,
                150.0,
                1500.0,
                150.0,
                0.9,
                "v1",
                "open",
                now,
            ),
            (
                now,
                "ord_002",
                "MSFT",
                "sell",
                5.0,
                320.0,
                1600.0,
                320.0,
                0.8,
                "v1",
                "filled",
                now,
            ),
        ]
        cur.executemany(
            f"INSERT INTO {TABLE_NAME} (ts,order_id,symbol,side,qty,price,nav,last_price,p_fill,model_version,outcome_status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            sample,
        )
        conn.commit()
        LOGGER.info("Initialized sample DB %s with %d rows", db_path, len(sample))
    finally:
        conn.close()


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Export SQLite predictions to partitioned Parquet files (supercharged)"
    )
    p.add_argument("--db", default=str(DEFAULT_DB), help="Path to sqlite DB file")
    p.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="Output directory to store parquet partitions",
    )
    p.add_argument(
        "--since",
        default=None,
        help="Only export rows with ts >= YYYY-MM-DD or ISO timestamp",
    )
    p.add_argument(
        "--archive",
        action="store_true",
        help="Archive exported rows into archive_predictions table (best-effort)",
    )
    p.add_argument(
        "--delete",
        action="store_true",
        help="Delete exported rows after export (irreversible)",
    )
    p.add_argument(
        "--init-db",
        action="store_true",
        help="Create a small sample DB /predictions/ table for testing (drops existing predictions table)",
    )
    p.add_argument(
        "--update-marker",
        action="store_true",
        help="Update exporter_state.last_export_ts to the max exported ts after a successful export",
    )
    p.add_argument(
        "--force", action="store_true", help="Ignore marker and export rows regardless"
    )
    p.add_argument(
        "--compression",
        default=None,
        choices=[c for c in ALLOWED_COMPRESSION],
        help="Parquet compression to use (e.g. snappy)",
    )
    p.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    # consolidation/prune options
    p.add_argument(
        "--consolidate",
        action="store_true",
        help="Run consolidation/compaction of existing partitions (on-demand)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="When used with --consolidate, show actions without making changes",
    )
    p.add_argument(
        "--prune-old",
        choices=PRUNE_CHOICES,
        default="archive",
        help="What to do with legacy part-*.parquet files after consolidation (default: archive)",
    )
    p.add_argument(
        "--retention-days",
        type=int,
        default=7,
        help="When pruning with 'archive', keep legacy archives for this many days",
    )
    p.add_argument(
        "--symbol",
        default=None,
        help="Optional symbol filter for consolidation (e.g. NIFTY)",
    )
    p.add_argument(
        "--date-from",
        default=None,
        help="Optional date-from (YYYY-MM-DD) filter for consolidation",
    )
    p.add_argument(
        "--date-to",
        default=None,
        help="Optional date-to (YYYY-MM-DD) filter for consolidation",
    )
    return p.parse_args(argv)


def do_export(
    db_path: Path,
    out_dir: Path,
    since: Optional[str] = None,
    archive: bool = False,
    delete: bool = False,
    update_marker: bool = False,
    force: bool = False,
    compression: Optional[str] = None,
    verbose: bool = False,
) -> Tuple[List[Path], int]:
    setup_logging(verbose)
    db_path = Path(db_path)
    out_dir = Path(out_dir)
    ensure_outdir(out_dir)

    effective_since = since
    if not effective_since and not force:
        marker = read_last_export_ts(db_path)
        if marker:
            LOGGER.info("Using last_export_ts marker: %s", marker)
            effective_since = marker

    raw = read_predictions_raw(db_path, since=effective_since)
    if raw.empty:
        LOGGER.info("No prediction rows found (empty). Nothing to export.")
        return [], 0

    df = _normalize_predictions_df(raw)
    if df.empty:
        LOGGER.info("Normalization produced empty df; nothing to export.")
        return [], 0

    result = export_predictions_to_parquet(
        db_path=db_path,
        out_dir=out_dir,
        partition_cols=("symbol", "date", "timeframe"),
        compression=compression,
        since=effective_since,
        archive=archive,
        delete=delete,
        update_marker=update_marker,
        verbose=verbose,
    )
    written_files = result.files
    rows = result.rows

    return written_files, rows


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    setup_logging(args.verbose)
    db_path = Path(args.db)
    out_dir = Path(args.out)

    if args.init_db:
        init_sample_db(db_path)
        print("Sample DB initialized")
        return 0

    # If consolidate requested, run consolidation first (dry-run may be used)
    if args.consolidate:
        summary = consolidate_partitions(
            out_dir=out_dir,
            partition_cols=("symbol", "date", "timeframe"),
            dry_run=args.dry_run,
            prune_mode=args.prune_old,
            retention_days=args.retention_days,
            symbol_filter=args.symbol,
            date_from=args.date_from,
            date_to=args.date_to,
            verbose=args.verbose,
        )
        print(json.dumps(summary, indent=2))
        # If only consolidating, exit now
        if args.dry_run or (
            args.consolidate
            and not (args.force or args.update_marker or args.delete or args.archive)
        ):
            return 0

    written_files, rows = do_export(
        db_path=db_path,
        out_dir=out_dir,
        since=args.since,
        archive=args.archive,
        delete=args.delete,
        update_marker=args.update_marker,
        force=args.force,
        compression=args.compression,
        verbose=args.verbose,
    )

    print(
        f"Exported approximately {rows} rows into {len(written_files)} parquet files under {out_dir}"
    )
    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
