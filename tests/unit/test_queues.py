# tests/unit/test_queues.py
import pytest
import asyncio
import os
from infra.queues import PersistentQueue

@pytest.mark.asyncio
async def test_queue_put_get(tmp_path):
    p = tmp_path / "qfile.ndjson"
    q = PersistentQueue(str(p))
    await q.put({"a": 1})
    assert q.qsize() == 1
    item = await q.get()
    assert item == {"a": 1}
