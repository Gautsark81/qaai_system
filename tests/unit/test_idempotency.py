# tests/unit/test_idempotency.py
import os
import tempfile
from data.idempotency import SqliteIdempotency, IdempotencyStore

def test_sqlite_claim_release():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    try:
        s = SqliteIdempotency(path)
        assert s.claim("k1") is True
        assert s.claim("k1") is False
        s.release("k1")
        assert s.claim("k1") is True
    finally:
        os.remove(path)

def test_store_fallback_sqlite_only():
    s = IdempotencyStore(sqlite_path=":memory:", redis_client=None)
    assert s.claim("x") is True
    assert s.claim("x") is False
