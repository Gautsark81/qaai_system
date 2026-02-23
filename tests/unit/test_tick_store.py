import os
import asyncio
import tempfile
import shutil
import pytest
from data.tick_store import TickStore

@pytest.mark.asyncio
async def test_tick_store_write_and_fetch(tmp_path):
    db_path = str(tmp_path / "ticks_test.db")
    ts = TickStore(db_path=db_path)
    try:
        sample = {"security_id": 1333, "ltp": 992.8, "ltq": 5, "volume": 1000, "timestamp": "11:02:23", "raw_type": "Quote Data"}
        await ts.write_tick(sample)
        await ts.write_tick({**sample, "ltp": 993.2})
        # small sleep to ensure executor finished (shouldn't be necessary but safe)
        await asyncio.sleep(0.01)
        rows = await ts.fetch_ticks(limit=10)
        assert len(rows) >= 2
        # newest row first (DESC)
        assert rows[0]["ltp"] in (993.2, 993.2)
        assert rows[0]["raw"]["security_id"] == 1333
    finally:
        ts.close()
        if os.path.exists(db_path):
            os.remove(db_path)

def test_export_parquet(tmp_path):
    db_path = str(tmp_path / "ticks_export.db")
    ts = TickStore(db_path=db_path)
    try:
        # write couple of ticks synchronously via executor wrapper
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ts.write_tick({"security_id": 1, "ltp": 1.1, "raw_type": "Ticker Data", "timestamp": "t"}))
        loop.run_until_complete(ts.write_tick({"security_id": 2, "ltp": 2.2, "raw_type": "Quote Data", "timestamp": "t2"}))
        # export – requires pandas
        out_path = str(tmp_path / "ticks.parquet")
        try:
            ts.export_to_parquet(out_path)
        except RuntimeError:
            pytest.skip("pandas not available for parquet export")
        assert os.path.exists(out_path)
    finally:
        ts.close()
        if os.path.exists(db_path):
            os.remove(db_path)
