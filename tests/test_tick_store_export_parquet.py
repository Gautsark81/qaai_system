# tests/test_tick_store_export_parquet.py
import tempfile
import os
import pytest
from data.tick_store import TickStore

@pytest.mark.skipif(os.environ.get("CI_SKIP_PANDAS", "0") == "1", reason="Skip parquet export in CI without pandas")
def test_export_parquet_smoke(tmp_path):
    ts = TickStore(db_path=":memory:")
    ts.append_tick("P", {"timestamp": 1234, "price": 10, "size": 1, "meta": {"a": 1}})
    out = tmp_path / "ticks.parquet"
    ts.export_to_parquet(str(out))
    assert out.exists()
    ts.close()
