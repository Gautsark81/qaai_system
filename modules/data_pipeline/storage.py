# modules/data_pipeline/storage.py
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import tempfile
import os
import json
import logging

logger = logging.getLogger(__name__)

# Optional import for S3 support (boto3)
try:
    import boto3  # type: ignore
    from botocore.exceptions import ClientError  # type: ignore
    HAS_BOTO3 = True
except Exception:
    HAS_BOTO3 = False


def _atomic_write_parquet(df: pd.DataFrame, out_path: Path, index: bool = True):
    out_path.parent.mkdir(parents=True, exist_ok=True)
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


class LocalStore:
    """
    Local disk store. API is intentionally small and consistent with S3Store.
    """

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def path_for_raw(self, symbol: str, date_partition: str) -> Path:
        dest = self.base_dir / "raw" / symbol / f"date={date_partition}"
        return dest / f"{symbol}.parquet"

    def write_parquet(self, df: pd.DataFrame, out_path: Path) -> Path:
        _atomic_write_parquet(df, out_path)
        return out_path

    def read_parquet(self, in_path: Path) -> pd.DataFrame:
        if not in_path.exists():
            return pd.DataFrame()
        return pd.read_parquet(in_path)

    def write_manifest(self, manifest_path: Path, manifest: Dict[str, Any]) -> Path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False))
        return manifest_path


class S3Store:
    """
    Simple S3 adapter. s3_uri examples:
       s3://my-bucket/path/to/file.parquet
    """

    def __init__(self, region_name: Optional[str] = None, session: Optional[Any] = None):
        if not HAS_BOTO3:
            raise RuntimeError("boto3 is required for S3Store")
        self.session = session or boto3.session.Session(region_name=region_name)
        self.s3 = self.session.client("s3")

    def _parse_uri(self, s3_uri: str):
        if not s3_uri.startswith("s3://"):
            raise ValueError("S3 URI must start with s3://")
        rest = s3_uri[len("s3://"):]
        parts = rest.split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
        return bucket, key

    def write_parquet(self, df: pd.DataFrame, s3_uri: str) -> str:
        bucket, key = self._parse_uri(s3_uri)
        # write locally then upload for atomic semantics
        tmp = Path(tempfile.mkstemp(prefix="tmp_parquet_")[1])
        try:
            df.to_parquet(tmp, index=True)
            self.s3.upload_file(str(tmp), bucket, key)
        finally:
            try:
                tmp.unlink()
            except Exception:
                pass
        return s3_uri

    def read_parquet(self, s3_uri: str) -> pd.DataFrame:
        bucket, key = self._parse_uri(s3_uri)
        tmp = Path(tempfile.mkstemp(prefix="tmp_parquet_")[1])
        try:
            self.s3.download_file(bucket, key, str(tmp))
            return pd.read_parquet(tmp)
        finally:
            try:
                tmp.unlink()
            except Exception:
                pass

    def write_manifest(self, s3_uri: str, manifest: Dict[str, Any]) -> str:
        bucket, key = self._parse_uri(s3_uri)
        manifest_key = key.rstrip("/") + ".manifest.json"
        body = json.dumps(manifest, ensure_ascii=False)
        self.s3.put_object(Bucket=bucket, Key=manifest_key, Body=body.encode("utf-8"))
        return f"s3://{bucket}/{manifest_key}"
