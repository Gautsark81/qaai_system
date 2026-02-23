# tests/test_storage_adapter.py
import pytest
import pandas as pd
from pathlib import Path
from modules.data_pipeline.storage import LocalStore
import tempfile
import os
import shutil

def test_local_store_write_and_read(tmp_path):
    df = pd.DataFrame({"open":[1.0,2.0],"high":[1.1,2.1],"low":[0.9,1.9],"close":[1.05,2.05],"volume":[100,200]},
                      index=pd.to_datetime(["2025-01-01","2025-01-02"]))
    base = tmp_path / "store"
    ls = LocalStore(base)
    outpath = ls.path_for_raw("FOO", "2025-01-02")
    outpath.parent.mkdir(parents=True, exist_ok=True)
    p = ls.write_parquet(df, outpath)
    assert p.exists()
    read = ls.read_parquet(p)
    assert list(read["open"]) == [1.0,2.0]

def test_write_manifest(tmp_path):
    base = tmp_path / "store"
    ls = LocalStore(base)
    manifest_path = base / "raw" / "FOO" / "date=2025-01-02" / "FOO.manifest.json"
    manifest = {"symbol":"FOO","rows":2,"date":"2025-01-02"}
    p = ls.write_manifest(manifest_path, manifest)
    assert p.exists()
    txt = p.read_text()
    assert '"symbol": "FOO"' in txt
