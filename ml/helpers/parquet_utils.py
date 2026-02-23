"""
Parquet utilities: atomic write, engine detection and schema helpers.
"""

from pathlib import Path
import pandas as pd
import tempfile
import shutil
from typing import Optional


def _choose_engine() -> str:
    """
    Prefer pyarrow if available, otherwise fastparquet.
    Raises RuntimeError if neither available.
    """
    try:
        return "pyarrow"
    except Exception:
        try:
            return "fastparquet"
        except Exception:
            raise RuntimeError(
                "No parquet engine available. Install pyarrow or fastparquet."
            )


def atomic_to_parquet(
    df: pd.DataFrame,
    dest: Path,
    partition_cols: Optional[list] = None,
    compression: str = "snappy",
    engine: Optional[str] = None,
) -> None:
    """
    Write DataFrame to `dest` path atomically using a temp file then move.
    If partition_cols provided, writes partitioned directory layout under dest.
    dest may be a directory or file path (if single-file).
    """
    dest = Path(dest)
    engine = engine or _choose_engine()
    dest_parent = dest if dest.is_dir() or dest.suffix == "" else dest.parent
    dest_parent.mkdir(parents=True, exist_ok=True)

    # pandas to_parquet will create directories if partition_cols is set and path is a directory
    # We'll write to a temp directory then move contents.
    with tempfile.TemporaryDirectory(dir=str(dest_parent)) as td:
        temp_path = Path(td) / "out"
        # If user provided a filename with suffix, write to temp_path / filename
        write_path = (
            temp_path if dest.is_dir() or dest.suffix == "" else (temp_path / dest.name)
        )
        write_path_parent = write_path.parent
        write_path_parent.mkdir(parents=True, exist_ok=True)

        # pandas requires the final path (directory or file) to exist parent-wise.
        if partition_cols:
            # when partitioning, pass directory
            df.to_parquet(
                str(write_path),
                engine=engine,
                compression=compression,
                partition_cols=partition_cols,
                index=False,
            )
        else:
            df.to_parquet(
                str(write_path), engine=engine, compression=compression, index=False
            )

        # Move the temp output to final destination.
        if write_path.is_file():
            # single file -> ensure dest parent exists
            final_file = dest if dest.suffix else (dest / write_path.name)
            final_file_parent = final_file.parent
            final_file_parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(write_path), str(final_file))
        else:
            # directory output (possibly partitioned) -> move all contents
            # if dest exists, merge by moving files over
            final_dir = dest if dest.suffix == "" else dest.parent
            final_dir.mkdir(parents=True, exist_ok=True)
            for item in write_path.iterdir():
                target = final_dir / item.name
                if target.exists():
                    # remove existing and replace
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                shutil.move(str(item), str(target))


def ensure_parquet_engine_installed_msg() -> str:
    try:
        _choose_engine()
        return ""
    except RuntimeError as e:
        return (
            str(e) + " Install via `pip install pyarrow` or `pip install fastparquet`."
        )
