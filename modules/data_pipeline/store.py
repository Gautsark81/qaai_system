from pathlib import Path
import pandas as pd
import os
import tempfile
import json
from typing import Optional

def _ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def _atomic_write_parquet(df: pd.DataFrame, out_path: Path, index=True):
    _ensure_dir(out_path.parent)
    tmp_fd, tmp_path = tempfile.mkstemp(prefix="tmp_parquet_", dir=str(out_path.parent))
    os.close(tmp_fd)
    tmp_path = Path(tmp_path)
    try:
        df.to_parquet(tmp_path, index=index)
        os.replace(tmp_path, out_path)
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass

def write_raw_ohlcv(symbol: str, df: pd.DataFrame, out_dir: Path, date_partition: Optional[str] = None) -> Path:
    out_dir = Path(out_dir)
    if date_partition is None:
        if len(df) == 0:
            date_partition = "empty"
        else:
            last = pd.to_datetime(df.index.max())
            date_partition = last.strftime("%Y-%m-%d")
    dest = out_dir / "raw" / symbol / f"date={date_partition}"
    dest.mkdir(parents=True, exist_ok=True)
    out_path = dest / f"{symbol}.parquet"
    _atomic_write_parquet(df, out_path)
    manifest = dest / f"{symbol}.manifest.json"
    manifest.write_text(json.dumps({"rows": len(df), "symbol": symbol, "date": date_partition}))
    return out_path

def read_raw_ohlcv(symbol: str, out_dir: Path, date_partition: Optional[str] = None) -> pd.DataFrame:
    out_dir = Path(out_dir)
    base = out_dir / "raw" / symbol
    if date_partition:
        p = base / f"date={date_partition}" / f"{symbol}.parquet"
        return pd.read_parquet(p) if p.exists() else pd.DataFrame()
    if not base.exists():
        return pd.DataFrame()
    parts = sorted(base.glob("date=*"))
    if not parts:
        return pd.DataFrame()
    latest = parts[-1] / f"{symbol}.parquet"
    return pd.read_parquet(latest) if latest.exists() else pd.DataFrame()

def write_features(symbol: str, df: pd.DataFrame, out_dir: Path, date_partition: Optional[str] = None) -> Path:
    out_dir = Path(out_dir)
    if date_partition is None:
        if len(df) == 0:
            date_partition = "empty"
        else:
            last = pd.to_datetime(df.index.max())
            date_partition = last.strftime("%Y-%m-%d")
    dest = out_dir / "features" / f"date={date_partition}"
    dest.mkdir(parents=True, exist_ok=True)
    out_path = dest / f"{symbol}.parquet"
    _atomic_write_parquet(df, out_path)
    return out_path

def read_features(symbol: str, out_dir: Path, date_partition: Optional[str] = None) -> pd.DataFrame:
    out_dir = Path(out_dir)
    base = out_dir / "features"
    if date_partition:
        p = base / f"date={date_partition}" / f"{symbol}.parquet"
        return pd.read_parquet(p) if p.exists() else pd.DataFrame()
    parts = sorted((base).glob("date=*"))
    if not parts:
        return pd.DataFrame()
    latest = parts[-1] / f"{symbol}.parquet"
    return pd.read_parquet(latest) if latest.exists() else pd.DataFrame()
