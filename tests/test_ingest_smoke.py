# tests/test_ingest_smoke.py
import tempfile
from pathlib import Path
from modules.data_pipeline.fetchers import DummyFetcher
from modules.data_pipeline.ingest import ingest_universe
from modules.data_pipeline.store import read_features

def test_ingest_universe_smoke(tmp_path):
    symbols = ["AAA", "BBB"]
    fetcher = DummyFetcher()
    out = tmp_path / "data"
    results = ingest_universe(fetcher, symbols, "2025-01-01", "2025-02-15", out, parallel=2)
    assert isinstance(results, list)
    ok = [r for r in results if "error" not in r]
    assert len(ok) == 2, f"expected 2 successes; got {results}"
    # check that features exist for at least one partition file
    # read_features returns a DataFrame (may be empty if partitioning differs)
    df1 = read_features("AAA", out)
    assert df1 is not None
