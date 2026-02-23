# streamlit_app/utils/export_helpers.py
"""
Canonical export helpers for streamlit_app.

- safe_to_ist(series): converts datetime-like pandas Series to tz-naive IST datetimes for Excel.
- load_overlay_data(source_csv): loads CSV (tests patch this name).
- sanitize_datetimes_for_excel(df): converts datetime-like columns.
- generate_export_filename(output_name=None, out_dir=None): deterministic filename generator.
- export_df_to_excel(df, output_path, index=False, sheet_name="..."): atomic .xlsx write.
- run_overlay_export(source_csv=None, output_name=None): returns status string.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Union
from zoneinfo import ZoneInfo
import pandas as pd
import tempfile
import os
import datetime
import logging

logger = logging.getLogger("streamlit_app.utils.export_helpers")

IST_ZONE = ZoneInfo("Asia/Kolkata")
SUCCESS_PREFIX = "EXPORT_SUCCESS"
FAIL_PREFIX = "EXPORT_FAIL"


def safe_to_ist(series: Union[pd.Series, pd.DatetimeIndex, list]) -> pd.Series:
    """
    Convert a pandas Series (datetime-like) to tz-naive datetimes in IST suitable for Excel.

    Behavior:
      - If values are tz-naive → assume UTC then convert to IST.
      - If tz-aware → convert to IST.
      - If values cannot be parsed → NaT.
    """
    s = pd.to_datetime(series, errors="coerce")

    if isinstance(s, pd.DatetimeIndex):
        s = pd.Series(s)

    try:
        # For pandas >= 2.2 the recommended check for tz-aware dtypes is using DatetimeTZDtype
        # but here we just attempt to use .dt accessor safely
        if s.dt.tz is None:
            s = s.dt.tz_localize("UTC", ambiguous="NaT", nonexistent="shift_forward")
        s = s.dt.tz_convert(IST_ZONE).dt.tz_localize(None)
    except Exception:
        # Per-element fallback
        def _fallback(x):
            if pd.isna(x):
                return pd.NaT
            try:
                dt = pd.to_datetime(x)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                return dt.astimezone(IST_ZONE).replace(tzinfo=None)
            except Exception:
                return pd.NaT

        s = s.apply(_fallback)

    return s


def load_overlay_data(source_csv: Union[str, Path]) -> pd.DataFrame:
    """
    Load overlay CSV into a DataFrame. Tests expect this function name and sometimes patch it.
    Raises FileNotFoundError if the file does not exist.
    """
    p = Path(source_csv)
    if not p.exists():
        raise FileNotFoundError(f"Overlay source not found: {p}")
    df = pd.read_csv(p)
    # If tests expect a 'timestamp' or 'ts' column, keep it flexible:
    if "ts" not in df.columns and "timestamp" not in df.columns:
        for c in df.columns:
            try:
                # try parse first few rows to determine datetime-like
                sample = pd.to_datetime(df[c].dropna().head(5), errors="coerce")
                if sample.notna().any():
                    df = df.rename(columns={c: "timestamp"})
                    break
            except Exception:
                continue
    logger.info("Loading overlay data from provided path: %s", p)
    return df


# Backwards-compatible alias used earlier
def load_overlay_source(source_csv: Union[str, Path]) -> pd.DataFrame:
    return load_overlay_data(source_csv)


def sanitize_datetimes_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert any datetime-like columns to tz-naive IST datetimes (suitable for Excel).
    Uses safe_to_ist for conversions; leaves other columns unchanged.
    """
    df_copy = df.copy()
    for col in df_copy.columns:
        try:
            dtype = df_copy[col].dtype
            # Prefer explicit DatetimeTZDtype check for tz-aware
            is_tz = False
            try:
                from pandas import DatetimeTZDtype  # type: ignore

                is_tz = isinstance(dtype, DatetimeTZDtype)
            except Exception:
                # fallback: use legacy helper if not available
                is_tz = pd.api.types.is_datetime64tz_dtype(dtype)

            if pd.api.types.is_datetime64_any_dtype(dtype) or is_tz:
                df_copy[col] = safe_to_ist(df_copy[col])
            else:
                sample = df_copy[col].dropna().head(5)
                if not sample.empty:
                    coerced = pd.to_datetime(sample, errors="coerce")
                    if coerced.notna().sum() >= 1:
                        df_copy[col] = safe_to_ist(df_copy[col])
        except Exception:
            # If conversion fails for some column, leave it untouched.
            continue
    return df_copy


def generate_export_filename(
    output_name: Optional[str] = None, out_dir: Optional[Union[str, Path]] = None
) -> Path:
    """
    Generate a deterministic export path. Default out_dir = cwd/exports.
    """
    if out_dir is None:
        out_dir = Path.cwd() / "exports"
    else:
        out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if output_name:
        out_path = out_dir / output_name
    else:
        stamp = pd.Timestamp.utcnow().strftime("%Y%m%dT%H%M%SZ")
        out_path = out_dir / f"overlay_export_{stamp}.xlsx"
    return out_path.resolve()


def export_df_to_excel(
    df: pd.DataFrame,
    output_path: Union[str, Path],
    index: bool = False,
    sheet_name: str = "sheet1",
) -> Path:
    """
    Safely write DataFrame to an Excel file using an atomic write:
    - create a temporary file with .xlsx suffix in the same directory
    - write to it via pandas.ExcelWriter (openpyxl)
    - os.replace into final path
    """
    outp = Path(output_path)
    outp.parent.mkdir(parents=True, exist_ok=True)

    # ensure pandas ExcelWriter sees a supported extension
    fd, tmp = tempfile.mkstemp(dir=str(outp.parent), suffix=".xlsx")
    os.close(fd)
    try:
        df_to_write = sanitize_datetimes_for_excel(df)
        with pd.ExcelWriter(
            tmp, engine="openpyxl", datetime_format="yyyy-mm-dd hh:mm:ss"
        ) as writer:
            df_to_write.to_excel(writer, index=index, sheet_name=sheet_name)
        os.replace(tmp, str(outp))
        logger.info("Exported DataFrame to Excel: %s", outp.as_posix())
        return outp.resolve()
    finally:
        try:
            if Path(tmp).exists():
                Path(tmp).unlink()
        except Exception:
            pass


def run_overlay_export(
    source_csv: Optional[Union[str, Path]] = None, output_name: Optional[str] = None
) -> str:
    """
    Test-friendly overlay export entrypoint.
    Returns "EXPORT_SUCCESS: <path>" or "EXPORT_FAIL: <error>"
    """
    try:
        if source_csv is None:
            source_csv = Path.cwd() / "overlay.csv"
        df = load_overlay_data(source_csv)
        # normalize timestamp/ts column names
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")

        output_path = generate_export_filename(
            output_name, out_dir=Path.cwd() / "exports"
        )
        created = export_df_to_excel(df, output_path)
        return f"{SUCCESS_PREFIX}: {created.as_posix()}"
    except Exception as exc:
        logger.exception("run_overlay_export failed")
        return f"{FAIL_PREFIX}: {exc}"


__all__ = [
    "safe_to_ist",
    "load_overlay_data",
    "load_overlay_source",
    "sanitize_datetimes_for_excel",
    "generate_export_filename",
    "export_df_to_excel",
    "run_overlay_export",
    "SUCCESS_PREFIX",
    "FAIL_PREFIX",
]
